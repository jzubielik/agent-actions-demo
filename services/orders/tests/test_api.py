def test_a_new_order_is_a_draft_with_its_amounts(client, new_order):
    response = client.post("/orders", json=new_order)
    assert response.status_code == 201
    order = response.json()
    assert order["status"] == "draft"
    assert (order["subtotal_minor"], order["discount_minor"], order["total_minor"]) == (3097, 0, 3097)
    assert [item["sku"] for item in order["items"]] == ["book", "pen"]


def test_a_discount_code_lowers_the_total(client, new_order):
    order = client.post("/orders", json={**new_order, "discount_code": "SPRING10"}).json()
    assert (order["discount_minor"], order["total_minor"]) == (310, 2787)


def test_an_unknown_or_inactive_code_is_refused_and_nothing_is_stored(client, new_order):
    for code in ("NOPE", "OLD50"):
        assert client.post("/orders", json={**new_order, "discount_code": code}).status_code == 422
    assert client.get("/orders", params={"customer_id": "c-1"}).json() == []


def test_an_order_needs_a_line_and_sane_values(client, new_order):
    assert client.post("/orders", json={**new_order, "items": []}).status_code == 422
    assert client.post("/orders", json={**new_order, "currency": "eur"}).status_code == 422
    bad_line = {"sku": "book", "quantity": 0, "unit_price_minor": 100}
    assert client.post("/orders", json={**new_order, "items": [bad_line]}).status_code == 422


def test_an_order_is_read_by_its_id(client, new_order):
    created = client.post("/orders", json=new_order).json()
    assert client.get(f"/orders/{created['id']}").json() == created
    assert client.get("/orders/missing").status_code == 404


def test_orders_are_listed_for_one_customer_and_filtered_by_status(client, new_order):
    first = client.post("/orders", json=new_order).json()
    second = client.post("/orders", json=new_order).json()
    client.post("/orders", json={**new_order, "customer_id": "c-2"})
    client.post(f"/orders/{second['id']}/place")
    listed = client.get("/orders", params={"customer_id": "c-1"}).json()
    assert {order["id"] for order in listed} == {first["id"], second["id"]}
    placed = client.get("/orders", params={"customer_id": "c-1", "status": "placed"}).json()
    assert [order["id"] for order in placed] == [second["id"]]
    assert len(client.get("/orders", params={"customer_id": "c-1", "limit": 1}).json()) == 1
    assert client.get("/orders").status_code == 422


def test_an_order_moves_from_draft_to_placed_to_paid(client, new_order):
    order_id = client.post("/orders", json=new_order).json()["id"]
    assert client.post(f"/orders/{order_id}/pay").status_code == 409
    assert client.post(f"/orders/{order_id}/place").json()["status"] == "placed"
    assert client.post(f"/orders/{order_id}/place").status_code == 409
    assert client.post(f"/orders/{order_id}/pay").json()["status"] == "paid"
    assert client.post("/orders/missing/place").status_code == 404


def test_a_draft_or_placed_order_can_be_cancelled(client, new_order):
    draft = client.post("/orders", json=new_order).json()["id"]
    placed = client.post("/orders", json=new_order).json()["id"]
    client.post(f"/orders/{placed}/place")
    for order_id in (draft, placed):
        assert client.post(f"/orders/{order_id}/cancel").json()["status"] == "cancelled"
    cancelled = client.get("/orders", params={"customer_id": "c-1", "status": "cancelled"}).json()
    assert {order["id"] for order in cancelled} == {draft, placed}


def test_a_paid_or_cancelled_order_stays_as_it_is(client, new_order):
    paid = client.post("/orders", json=new_order).json()["id"]
    client.post(f"/orders/{paid}/place")
    client.post(f"/orders/{paid}/pay")
    assert client.post(f"/orders/{paid}/cancel").status_code == 409
    assert client.get(f"/orders/{paid}").json()["status"] == "paid"
    cancelled = client.post("/orders", json=new_order).json()["id"]
    client.post(f"/orders/{cancelled}/cancel")
    for action in ("cancel", "place", "pay"):
        assert client.post(f"/orders/{cancelled}/{action}").status_code == 409
    assert client.post("/orders/missing/cancel").status_code == 404


def test_lines_cannot_outlive_their_order(client, new_order):
    order_id = client.post("/orders", json=new_order).json()["id"]
    conn = client.app.state.conn
    conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    assert conn.execute("SELECT count(*) FROM order_items").fetchone()[0] == 0
