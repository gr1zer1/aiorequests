import time

from aiorequests.http.request import Request
from aiorequests.http.response import Response


REQUEST_ITERATIONS = 10_000
RESPONSE_ITERATIONS = 10_000
MAX_SECONDS = 1.5


def test_request_serialization_speed():
    start = time.perf_counter()

    for index in range(REQUEST_ITERATIONS):
        Request(
            "post",
            f"https://example.com/items/{index}?active=true",
            headers={"Accept": "application/json"},
            body={"index": index, "name": "example"},
        ).to_bytes()

    elapsed = time.perf_counter() - start

    assert elapsed < MAX_SECONDS, (
        f"serialized {REQUEST_ITERATIONS} requests in {elapsed:.3f}s"
    )


def test_response_parsing_speed():
    payload = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: application/json\r\n"
        b"Content-Length: 26\r\n"
        b"\r\n"
        b'{"ok": true, "items": [1]}'
    )

    start = time.perf_counter()

    for _ in range(RESPONSE_ITERATIONS):
        Response.from_bytes(payload)

    elapsed = time.perf_counter() - start

    assert elapsed < MAX_SECONDS, (
        f"parsed {RESPONSE_ITERATIONS} responses in {elapsed:.3f}s"
    )
