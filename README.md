# aiorequests

`aiorequests` is a small educational asynchronous HTTP client written with Python's standard library. It shows how to build HTTP requests, open TCP/TLS connections with `asyncio`, reuse connections inside a session, and parse basic HTTP responses.

> The project is useful for learning how HTTP clients work internally. For production code, prefer mature clients such as `aiohttp` or `httpx`.

## Features

- Async API based on `asyncio`
- HTTP and HTTPS connections
- Session-level connection reuse
- Common HTTP methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
- Default client headers and per-request headers
- String and JSON request bodies
- Basic response parsing with automatic JSON decoding
- Custom exceptions for DNS, connection, timeout, and port errors

## Requirements

- Python 3.10+
- No external dependencies

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/aiorequests.git
cd aiorequests
```

Run the example:

```bash
python main.py
```

## Quick Start

```python
import asyncio
from client import Client


async def main():
    client = Client(headers={"User-Agent": "aiorequests/0.1"})

    async with client as session:
        response = await session.get("https://httpbin.org/get")

    print(response.status_code)
    print(response.headers)
    print(response.body)


asyncio.run(main())
```

## Sending Data

JSON body:

```python
async with Client() as session:
    response = await session.post(
        "https://httpbin.org/post",
        body={"name": "Alice", "active": True},
        headers={"Accept": "application/json"},
    )

print(response.body)
```

Plain text body:

```python
async with Client() as session:
    response = await session.post(
        "https://httpbin.org/post",
        body="hello",
    )

print(response.status)
```

## API Overview

### `Client`

Creates a client and stores default headers.

```python
client = Client(headers={"Authorization": "Bearer token"})
```

Use it as an async context manager:

```python
async with Client() as session:
    response = await session.get("https://example.com")
```

### `Session`

Available request methods:

- `get(url, headers=None, n=4096)`
- `post(url, body=None, headers=None, n=4096)`
- `put(url, body=None, headers=None, n=4096)`
- `patch(url, body=None, headers=None, n=4096)`
- `delete(url, body=None, headers=None, n=4096)`

### `Response`

Response objects contain:

- `schema`: HTTP version, for example `HTTP/1.1`
- `status_code`: numeric status code
- `status`: status text, for example `200 OK`
- `headers`: response headers as a dictionary
- `body`: parsed JSON, text, or `None`

### Exceptions

All custom exceptions inherit from `AsyncHttpError`:

- `ConnectError`
- `TimeoutError`
- `DNSError`
- `PortError`

## Project Structure

```text
.
├── client.py       # Client context manager
├── connection.py   # TCP/TLS connection handling
├── exception.py    # Custom exception classes
├── main.py         # Usage example
├── request.py      # HTTP request builder
├── response.py     # HTTP response parser
└── session.py      # Request methods and connection reuse
```

## Current Limitations

- Only basic HTTP/1.1 response parsing is implemented.
- Responses are expected to use `Content-Length`.
- Chunked transfer encoding is not supported yet.
- Redirect handling, cookies, retries, and connection pooling by host are not implemented yet.
- The project is not packaged for PyPI yet.

## Roadmap

- Add tests for request and response parsing
- Support chunked responses
- Improve HTTPS timeout handling
- Add redirect support
- Add `pyproject.toml` packaging metadata
- Add CI for linting and tests

## License

No license file is included yet. Add a license before distributing or accepting external contributions.
