import pytest

from aiorequests.core.client import Client
from aiorequests.errors.exception import ConnectError
from aiorequests.http.response import Response


class FakeConnection:
    created = []

    def __init__(self, url):
        self.url = url
        self.connected = False
        self.closed = False
        self.sent = []
        self.recv_chunks = [
            b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 11\r\n\r\nhel",
            b"lo world",
        ]
        FakeConnection.created.append(self)

    @classmethod
    def create_conn_from_url(cls, url):
        return cls(url)

    async def connect(self):
        self.connected = True

    async def send(self, data):
        self.sent.append(data)

    async def recv(self, n=4096):
        return self.recv_chunks.pop(0)

    def close(self):
        self.closed = True


@pytest.fixture
def fake_connection(monkeypatch):
    FakeConnection.created = []
    monkeypatch.setattr("aiorequests.core.session.Connection", FakeConnection)
    return FakeConnection


@pytest.mark.asyncio
async def test_request_reads_body_split_across_multiple_recv_calls(fake_connection):
    client = Client(headers={"User-Agent": "tests"})

    response = await client.session.get(
        "http://example.com/hello",
        headers={"Accept": "text/plain"},
        n=4,
    )

    assert isinstance(response, Response)
    assert response.status_code == 200
    assert response.body == "hello world"
    assert len(fake_connection.created) == 1
    assert fake_connection.created[0].connected is True
    assert b"User-Agent: tests\r\n" in fake_connection.created[0].sent[0]
    assert b"Accept: text/plain\r\n" in fake_connection.created[0].sent[0]


@pytest.mark.asyncio
async def test_reuses_connection_for_same_url(fake_connection):
    client = Client()

    await client.session.get("http://example.com/hello")
    fake_connection.created[0].recv_chunks = [
        b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 2\r\n\r\nok",
    ]
    await client.session.get("http://example.com/hello")

    assert len(fake_connection.created) == 1
    assert len(fake_connection.created[0].sent) == 2


@pytest.mark.asyncio
async def test_get_request_adds_query_params(fake_connection):
    client = Client()

    await client.session.get(
        "http://example.com/search",
        params={"q": "python", "page": "1"},
    )

    assert len(fake_connection.created) == 1
    assert fake_connection.created[0].url == "http://example.com/search?q=python&page=1"
    assert fake_connection.created[0].sent[0].startswith(
        b"GET /search?q=python&page=1 HTTP/1.1\r\n"
    )


@pytest.mark.asyncio
async def test_client_context_closes_connections(fake_connection):
    client = Client()

    async with client as session:
        await session.get("http://example.com/hello")

    assert fake_connection.created[0].closed is True


@pytest.mark.asyncio
async def test_retries_retryable_status_with_new_connection(monkeypatch):
    class RetryStatusConnection(FakeConnection):
        responses = [
            [b"HTTP/1.1 503 Service Unavailable\r\nContent-Length: 0\r\n\r\n"],
            [b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 2\r\n\r\nok"],
        ]

        def __init__(self, url):
            super().__init__(url)
            self.recv_chunks = self.responses.pop(0)

    FakeConnection.created = []
    monkeypatch.setattr("aiorequests.core.session.Connection", RetryStatusConnection)

    client = Client()
    response = await client.session.get("http://example.com/hello", retries=1)

    assert response.status_code == 200
    assert response.body == "ok"
    assert len(FakeConnection.created) == 2
    assert FakeConnection.created[0].closed is True


@pytest.mark.asyncio
async def test_retries_connection_error_with_new_connection(monkeypatch):
    class RetryConnectConnection(FakeConnection):
        connect_calls = 0

        async def connect(self):
            type(self).connect_calls += 1
            if self.connect_calls == 1:
                raise ConnectError("temporary failure")
            self.connected = True

    FakeConnection.created = []
    monkeypatch.setattr("aiorequests.core.session.Connection", RetryConnectConnection)

    client = Client()
    response = await client.session.get("http://example.com/hello", retries=1)

    assert response.status_code == 200
    assert len(FakeConnection.created) == 2
    assert FakeConnection.created[0].closed is True
    assert FakeConnection.created[1].connected is True
