import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import contract  # noqa: E402

SPEC = contract.load(contract.CONTRACT)


def changed(change) -> list[str]:
    new = copy.deepcopy(SPEC)
    change(new["components"]["schemas"], new["paths"])
    return contract.breaking(SPEC, new)


def test_the_contract_is_what_the_service_serves():
    assert SPEC == contract.served()


def test_every_consumer_reads_fields_the_contract_has():
    assert contract.unknown_fields(SPEC, contract.load(contract.CONSUMERS)) == []


def test_a_field_a_consumer_reads_must_exist():
    consumers = {"billing": {"GET /orders/{order_id}": ["items[].tax"], "GET /invoices": ["id"]}}
    assert contract.unknown_fields(SPEC, consumers) == [
        "billing reads items[].tax of GET /orders/{order_id}, which the contract does not have",
        "billing calls GET /invoices, which the contract does not have",
    ]


def test_an_unchanged_contract_and_an_added_field_break_nothing():
    assert contract.breaking(SPEC, SPEC) == []
    assert changed(lambda schemas, paths: schemas["Order"]["properties"].update(note={"type": "string"})) == []


def test_a_removed_response_field_breaks_every_operation_that_returns_it():
    problems = changed(lambda schemas, paths: schemas["Order"]["properties"].pop("discount_minor"))
    assert "GET /orders/{order_id}: response field discount_minor is gone" in problems
    assert "GET /orders: response field [].discount_minor is gone" in problems


def test_a_retyped_field_a_new_enum_value_and_a_removed_operation_break():
    assert "GET /orders/{order_id}: response field items[].quantity changed from integer to string" in changed(
        lambda schemas, paths: schemas["Item"]["properties"].update(quantity={"type": "string"})
    )
    assert "GET /orders/{order_id}: response field status can now be refunded" in changed(
        lambda schemas, paths: schemas["Status"]["enum"].append("refunded")
    )
    assert changed(lambda schemas, paths: paths.pop("/orders/{order_id}/pay")) == ["POST /orders/{order_id}/pay: the operation is gone"]


def test_a_new_required_request_field_or_parameter_breaks():
    assert changed(lambda schemas, paths: schemas["NewOrder"]["required"].append("discount_code")) == [
        "POST /orders: request field discount_code is now required"
    ]
    status = next(p for p in SPEC["paths"]["/orders"]["get"]["parameters"] if p["name"] == "status")
    index = SPEC["paths"]["/orders"]["get"]["parameters"].index(status)
    assert changed(lambda schemas, paths: paths["/orders"]["get"]["parameters"][index].update(required=True)) == [
        "GET /orders: parameter status is now required"
    ]
