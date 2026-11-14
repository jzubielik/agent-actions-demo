"""Reads and writes orders. Every statement takes its values as parameters."""
import sqlite3
import uuid
from datetime import datetime, timezone

from . import pricing
from .models import Item, NewOrder, Order, Status


class UnknownDiscount(Exception):
    pass


class NotFound(Exception):
    pass


class WrongStatus(Exception):
    pass


# Which status an order may move to.
TRANSITIONS = {
    Status.draft: {Status.placed, Status.cancelled},
    Status.placed: {Status.paid, Status.cancelled},
}


def _percent(conn: sqlite3.Connection, code: str | None) -> int:
    if code is None:
        return 0
    # A code is valid up to and including its expiry day, in UTC.
    row = conn.execute(
        "SELECT percent FROM discount_codes WHERE code = ? AND active = 1"
        " AND (expires_at IS NULL OR expires_at >= date('now'))",
        (code,),
    ).fetchone()
    if row is None:
        raise UnknownDiscount(code)
    return row["percent"]


def _order(conn: sqlite3.Connection, row: sqlite3.Row) -> Order:
    items = conn.execute(
        "SELECT sku, quantity, unit_price_minor FROM order_items WHERE order_id = ? ORDER BY position", (row["id"],)
    ).fetchall()
    return Order(**dict(row), items=[Item(**dict(item)) for item in items])


def create(conn: sqlite3.Connection, new: NewOrder) -> Order:
    percent = _percent(conn, new.discount_code)
    before, off, total = pricing.totals([(item.quantity, item.unit_price_minor) for item in new.items], percent)
    order_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    # The order and its lines are one unit: a reader never sees an order without lines.
    conn.execute("BEGIN")
    try:
        conn.execute(
            "INSERT INTO orders (id, customer_id, currency, status, discount_code, subtotal_minor, discount_minor,"
            " total_minor, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (order_id, new.customer_id, new.currency, Status.draft.value, new.discount_code, before, off, total, created_at),
        )
        conn.executemany(
            "INSERT INTO order_items (order_id, position, sku, quantity, unit_price_minor) VALUES (?, ?, ?, ?, ?)",
            [(order_id, position, item.sku, item.quantity, item.unit_price_minor) for position, item in enumerate(new.items)],
        )
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    return get(conn, order_id)


def get(conn: sqlite3.Connection, order_id: str) -> Order:
    row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        raise NotFound(order_id)
    return _order(conn, row)


def find(conn: sqlite3.Connection, customer_id: str, status: Status | None, limit: int) -> list[Order]:
    query = "SELECT * FROM orders WHERE customer_id = ?"
    values: list[str | int] = [customer_id]
    if status is not None:
        query += " AND status = ?"
        values.append(status.value)
    query += " ORDER BY created_at DESC, id LIMIT ?"
    values.append(limit)
    return [_order(conn, row) for row in conn.execute(query, values).fetchall()]


def move(conn: sqlite3.Connection, order_id: str, to: Status) -> Order:
    """Moves the order to a new status, if its current one allows it."""
    current = get(conn, order_id).status
    if to not in TRANSITIONS.get(current, set()):
        raise WrongStatus(f"an order that is {current.value} cannot become {to.value}")
    # The status is part of the condition: two requests at once cannot both move the order.
    changed = conn.execute(
        "UPDATE orders SET status = ? WHERE id = ? AND status = ?", (to.value, order_id, current.value)
    ).rowcount
    if changed == 0:
        raise WrongStatus(f"the order is no longer {current.value}")
    return get(conn, order_id)
