from aiorequests.http.response import Response


def test_parses_json_response():
    response = Response.from_bytes(
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: application/json\r\n"
        b"Content-Length: 12\r\n"
        b"\r\n"
        b'{"ok": true}'
    )

    assert response.schema == "HTTP/1.1"
    assert response.status_code == 200
    assert response.status == "200 OK"
    assert response.headers["Content-Type"] == "application/json"
    assert response.body == {"ok": True}


def test_parses_text_response():
    response = Response.from_bytes(
        b"HTTP/1.1 404 Not Found\r\n"
        b"Content-Type: text/plain\r\n"
        b"Content-Length: 7\r\n"
        b"\r\n"
        b"missing"
    )

    assert response.status_code == 404
    assert response.status == "404 Not Found"
    assert response.body == "missing"


def test_empty_or_untyped_body_is_none():
    response = Response.from_bytes(
        b"HTTP/1.1 204 No Content\r\n"
        b"Content-Length: 0\r\n"
        b"\r\n"
    )

    assert response.status_code == 204
    assert response.body is None
