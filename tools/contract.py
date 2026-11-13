"""Checks of the API contract in contracts/.

  python tools/contract.py export            write contracts/orders.openapi.yaml from the orders service
  python tools/contract.py snapshot          fail when that file differs from what the service serves
  python tools/contract.py consumers         fail when a consumer reads a field the contract does not have
  python tools/contract.py diff OLD.yaml     fail when the contract breaks a client of OLD.yaml

A breaking change is one that an existing client can notice: a removed operation, a removed or
retyped response field, a new required request field or parameter, a new value of an enum in a
response.
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTRACT = ROOT / "contracts" / "orders.openapi.yaml"
CONSUMERS = ROOT / "contracts" / "consumers.yaml"
METHODS = ("get", "post", "put", "patch", "delete")


def served() -> dict:
    sys.path.insert(0, str(ROOT / "services" / "orders"))
    from orders.app import create_app

    return create_app(":memory:").openapi()


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def resolve(spec: dict, schema: dict) -> dict:
    """Follows $ref and unwraps the "T or null" form the framework writes for optional fields."""
    while "$ref" in schema:
        schema = spec["components"]["schemas"][schema["$ref"].rsplit("/", 1)[-1]]
    options = [option for option in schema.get("anyOf", []) if option.get("type") != "null"]
    return resolve(spec, options[0]) if len(options) == 1 else schema


def operations(spec: dict) -> dict[str, dict]:
    return {
        f"{method.upper()} {path}": operation
        for path, item in spec.get("paths", {}).items()
        for method, operation in item.items()
        if method in METHODS
    }


def body(spec: dict, holder: dict) -> dict | None:
    schema = holder.get("content", {}).get("application/json", {}).get("schema")
    return None if schema is None else resolve(spec, schema)


def success(spec: dict, operation: dict) -> dict | None:
    for status, response in operation.get("responses", {}).items():
        if status.startswith("2"):
            return body(spec, response)
    return None


def fields(spec: dict, schema: dict | None, prefix: str = "") -> dict[str, dict]:
    """Every field of a schema by its path: "items[].sku" is sku of each element of items."""
    if schema is None:
        return {}
    if schema.get("type") == "array":
        return fields(spec, resolve(spec, schema["items"]), f"{prefix}[]" if prefix else "[]")
    found = {}
    for name, child in schema.get("properties", {}).items():
        child = resolve(spec, child)
        path = f"{prefix}.{name}" if prefix else name
        found[path] = child
        found.update(fields(spec, child, path))
    return found


def breaking(old: dict, new: dict) -> list[str]:
    problems = []
    new_operations = operations(new)
    for name, old_operation in operations(old).items():
        if name not in new_operations:
            problems.append(f"{name}: the operation is gone")
            continue
        new_operation = new_operations[name]
        new_fields = fields(new, success(new, new_operation))
        for path, old_field in fields(old, success(old, old_operation)).items():
            if path not in new_fields:
                problems.append(f"{name}: response field {path} is gone")
            elif old_field.get("type") != new_fields[path].get("type"):
                problems.append(f"{name}: response field {path} changed from {old_field.get('type')} to {new_fields[path].get('type')}")
            elif missing := set(new_fields[path].get("enum", [])) - set(old_field.get("enum", [])):
                problems.append(f"{name}: response field {path} can now be {', '.join(sorted(missing))}")
        old_request = body(old, old_operation.get("requestBody", {})) or {}
        new_request = body(new, new_operation.get("requestBody", {})) or {}
        for field in sorted(set(new_request.get("required", [])) - set(old_request.get("required", []))):
            problems.append(f"{name}: request field {field} is now required")
        old_params = {(p["name"], p["in"]) for p in old_operation.get("parameters", []) if p.get("required")}
        for parameter in new_operation.get("parameters", []):
            if parameter.get("required") and (parameter["name"], parameter["in"]) not in old_params:
                problems.append(f"{name}: parameter {parameter['name']} is now required")
    return problems


def unknown_fields(spec: dict, consumers: dict) -> list[str]:
    problems = []
    all_operations = operations(spec)
    for consumer, reads in consumers.items():
        for name, paths in reads.items():
            if name not in all_operations:
                problems.append(f"{consumer} calls {name}, which the contract does not have")
                continue
            known = fields(spec, success(spec, all_operations[name]))
            problems += [f"{consumer} reads {path} of {name}, which the contract does not have" for path in paths if path not in known]
    return problems


def main(argv: list[str]) -> int:
    command = argv[1] if len(argv) > 1 else ""
    if command == "export":
        CONTRACT.write_text(yaml.safe_dump(served(), sort_keys=True))
        return 0
    if command == "snapshot":
        problems = [] if load(CONTRACT) == served() else ["contracts/orders.openapi.yaml differs from the service; run: make contract"]
    elif command == "consumers":
        problems = unknown_fields(load(CONTRACT), load(CONSUMERS))
    elif command == "diff" and len(argv) == 3:
        problems = breaking(load(Path(argv[2])), load(CONTRACT))
    else:
        print(__doc__, file=sys.stderr)
        return 2
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
