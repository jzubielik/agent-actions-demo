"""MCP server with a snapshot of production numbers, for the reviewers of this repository.

Tools: table_stats (size and write load of a table) and recent_errors (errors of a service in the
last 24 hours). It speaks MCP over stdio with the standard library only, so the review job can
start it without installing anything.
"""
import json
import sys
from pathlib import Path

SNAPSHOT = json.loads((Path(__file__).resolve().parent / "snapshot.json").read_text())

TOOLS = [
    {
        "name": "table_stats",
        "description": "Rows, size and write load of a production table, and the longest lock its traffic tolerates.",
        "inputSchema": {
            "type": "object",
            "properties": {"table": {"type": "string", "description": "Table name, for example orders"}},
            "required": ["table"],
        },
    },
    {
        "name": "recent_errors",
        "description": "Errors a service raised in production in the last 24 hours, most frequent first.",
        "inputSchema": {
            "type": "object",
            "properties": {"service": {"type": "string", "description": "orders, billing or web"}},
            "required": ["service"],
        },
    },
]


def table_stats(table: str) -> dict:
    if table not in SNAPSHOT["tables"]:
        raise KeyError(f"unknown table {table}; known: {', '.join(sorted(SNAPSHOT['tables']))}")
    return {"table": table, "taken_at": SNAPSHOT["taken_at"], **SNAPSHOT["tables"][table]}


def recent_errors(service: str) -> dict:
    if service not in SNAPSHOT["errors"]:
        raise KeyError(f"unknown service {service}; known: {', '.join(sorted(SNAPSHOT['errors']))}")
    errors = sorted(SNAPSHOT["errors"][service], key=lambda error: -error["count_24h"])
    return {"service": service, "taken_at": SNAPSHOT["taken_at"], "errors": errors}


CALLS = {"table_stats": lambda args: table_stats(args["table"]), "recent_errors": lambda args: recent_errors(args["service"])}


def call(params: dict) -> dict:
    """The result of tools/call. A failed call is a result with isError, as the protocol asks."""
    name, arguments = params.get("name"), params.get("arguments") or {}
    try:
        if name not in CALLS:
            raise KeyError(f"unknown tool {name}")
        text = json.dumps(CALLS[name](arguments))
        return {"content": [{"type": "text", "text": text}]}
    except KeyError as error:
        return {"content": [{"type": "text", "text": str(error.args[0])}], "isError": True}


def handle(message: dict) -> dict | None:
    """The answer to one JSON-RPC message, or None for a notification."""
    method, request_id = message.get("method"), message.get("id")
    if request_id is None:
        return None
    if method == "initialize":
        result = {
            "protocolVersion": message.get("params", {}).get("protocolVersion", "2025-06-18"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "prod_stats", "version": "1"},
        }
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        result = call(message.get("params", {}))
    else:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": f"method not found: {method}"}}
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def main() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            answer = handle(json.loads(line))
        except json.JSONDecodeError:
            answer = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
        if answer is not None:
            sys.stdout.write(json.dumps(answer) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
