import json
import subprocess
import sys
from pathlib import Path

SERVER = Path(__file__).resolve().parents[1] / "prod_stats" / "server.py"


def talk(*messages: dict) -> list[dict]:
    """Starts the server, sends the messages and returns its answers."""
    lines = "".join(json.dumps({"jsonrpc": "2.0", **message}) + "\n" for message in messages)
    done = subprocess.run([sys.executable, str(SERVER)], input=lines, capture_output=True, text=True, timeout=10, check=True)
    return [json.loads(line) for line in done.stdout.splitlines()]


def tool(name: str, **arguments) -> dict:
    (answer,) = talk({"id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}})
    return answer["result"]


def test_the_handshake_names_the_server_and_notifications_get_no_answer():
    answers = talk(
        {"id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}}},
        {"method": "notifications/initialized"},
        {"id": 2, "method": "tools/list"},
    )
    assert [answer["id"] for answer in answers] == [1, 2]
    assert answers[0]["result"]["serverInfo"]["name"] == "prod_stats"
    assert [tool["name"] for tool in answers[1]["result"]["tools"]] == ["table_stats", "recent_errors"]


def test_table_stats_gives_the_numbers_of_a_table():
    stats = json.loads(tool("table_stats", table="orders")["content"][0]["text"])
    assert stats["rows"] > 1_000_000 and stats["writes_per_minute"] > 0 and stats["taken_at"]


def test_recent_errors_come_most_frequent_first():
    errors = json.loads(tool("recent_errors", service="billing")["content"][0]["text"])["errors"]
    assert [error["count_24h"] for error in errors] == sorted((error["count_24h"] for error in errors), reverse=True)


def test_an_unknown_table_or_tool_is_an_error_result_not_a_crash():
    assert tool("table_stats", table="nope")["isError"] is True
    assert tool("drop_table", table="orders")["isError"] is True


def test_an_unknown_method_is_a_json_rpc_error():
    (answer,) = talk({"id": 7, "method": "resources/list"})
    assert answer["error"]["code"] == -32601
