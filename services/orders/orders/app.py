"""HTTP API of the orders service."""
import os
import sqlite3
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query

from . import repository
from .db import connect
from .models import NewOrder, Order, Problem, Status


def create_app(database: str | None = None) -> FastAPI:
    app = FastAPI(title="Orders", version="1.0.0")
    conn = connect(database or os.environ.get("ORDERS_DATABASE", "orders.db"))
    app.state.conn = conn

    def db() -> sqlite3.Connection:
        return conn

    Db = Annotated[sqlite3.Connection, Depends(db)]

    # Every response is described here: the default text comes from Python's list of HTTP
    # statuses, which differs between versions, and the contract must not.
    not_found = {"model": Problem, "description": "No order with this id"}

    @app.post(
        "/orders",
        response_model=Order,
        status_code=201,
        responses={422: {"model": Problem, "description": "The order is not valid or its discount code is unknown"}},
    )
    def create_order(new: NewOrder, conn: Db) -> Order:
        try:
            return repository.create(conn, new)
        except repository.UnknownDiscount as error:
            raise HTTPException(422, f"unknown discount code: {error}") from error

    @app.get("/orders/{order_id}", response_model=Order, responses={404: not_found})
    def get_order(order_id: str, conn: Db) -> Order:
        try:
            return repository.get(conn, order_id)
        except repository.NotFound as error:
            raise HTTPException(404, "order not found") from error

    @app.get("/orders", response_model=list[Order])
    def list_orders(
        conn: Db,
        customer_id: Annotated[str, Query(min_length=1, max_length=64)],
        status: Status | None = None,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
    ) -> list[Order]:
        return repository.find(conn, customer_id, status, limit)

    def move(order_id: str, to: Status, conn: sqlite3.Connection) -> Order:
        try:
            return repository.move(conn, order_id, to)
        except repository.NotFound as error:
            raise HTTPException(404, "order not found") from error
        except repository.WrongStatus as error:
            raise HTTPException(409, str(error)) from error

    transition = {404: not_found, 409: {"model": Problem, "description": "The status of the order does not allow this"}}

    @app.post("/orders/{order_id}/place", response_model=Order, responses=transition)
    def place_order(order_id: str, conn: Db) -> Order:
        return move(order_id, Status.placed, conn)

    @app.post("/orders/{order_id}/pay", response_model=Order, responses=transition)
    def pay_order(order_id: str, conn: Db) -> Order:
        return move(order_id, Status.paid, conn)

    return app
