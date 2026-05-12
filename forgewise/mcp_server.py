from __future__ import annotations

import json
import sys
from typing import Any, BinaryIO

from forgewise.protocol import handle_json_rpc as _handle_json_rpc
from forgewise.tools import list_tools as _list_tools


def list_tools() -> list[dict[str, Any]]:
    return _list_tools()


def handle_json_rpc(message: dict[str, Any], *, tool_prefix: str = "") -> dict[str, Any]:
    return _handle_json_rpc(message, tool_prefix=tool_prefix)


def main() -> int:
    while True:
        payload = _read_content_length_message(sys.stdin.buffer)
        if payload is None:
            return 0
        response = handle_json_rpc(json.loads(payload))
        _write_content_length_message(sys.stdout.buffer, json.dumps(response, ensure_ascii=False))
        sys.stdout.flush()


def _read_content_length_message(stream: BinaryIO) -> str | None:
    headers: dict[str, str] = {}
    while True:
        raw = stream.readline()
        if raw == b"":
            return None
        line = raw.decode("ascii", errors="replace").strip()
        if not line:
            break
        key, _, value = line.partition(":")
        headers[key.lower()] = value.strip()
    length = int(headers.get("content-length", "0"))
    if length <= 0:
        return None
    return stream.read(length).decode("utf-8")


def _write_content_length_message(stream: BinaryIO, payload: str) -> None:
    data = payload.encode("utf-8")
    stream.write(f"Content-Length: {len(data)}\r\n\r\n".encode("ascii") + data)
