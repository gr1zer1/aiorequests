import json

import pytest

from aiorequests.errors.exception import PortError
from aiorequests.http.request import Request


def test_adds_default_scheme_host_and_root_path():
    request = Request("get", "example.com")

    assert request.url == "http://example.com"
    assert request.port == 80
    assert request.to_bytes() == b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"


def test_preserves_path_query_and_custom_headers():
    request = Request(
        "post",
        "https://example.com/search?q=python",
        headers={"Accept": "application/json"},
    )

    data = request.to_bytes()

    assert request.port == 443
    assert b"POST /search?q=python HTTP/1.1\r\n" in data
    assert b"Accept: application/json\r\n" in data
    assert b"Host: example.com\r\n" in data


def test_serializes_text_body():
    request = Request("post", "example.com/messages", body="hello")

    data = request.to_bytes()

    assert data.endswith(b"\r\n\r\nhello")
    assert b"Content-Type: text/plain; charset=utf-8\r\n" in data
    assert b"Content-Length: 5\r\n" in data


def test_serializes_json_body():
    body = {"name": "Alice", "active": True}
    request = Request("post", "example.com/users", body=body)

    head, raw_body = request.to_bytes().split(b"\r\n\r\n", 1)

    assert b"Content-Type: application/json\r\n" in head
    assert json.loads(raw_body.decode("utf-8")) == body
    assert f"Content-Length: {len(raw_body)}".encode() in head


def test_raises_port_error_for_unknown_scheme():
    request = Request("get", "ftp://example.com/file")

    with pytest.raises(PortError):
        _ = request.port
