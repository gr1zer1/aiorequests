import asyncio
import socket
import ssl

from aiorequests.errors.exception import ConnectError, DNSError, TimeoutError
from aiorequests.http.request import Request


class Connection:
    def __init__(self, host: str, port: int, schema: str):
        self.host: str = host
        self.port: int  = port
        self.schema = schema
        self._sock: socket.socket | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self.tls_transport: asyncio.Transport | None = None
        self.protocol: MyProtocol | None = None

    @classmethod
    def from_request(cls,request:Request):
        return cls(request.parsed_url.hostname, request.port, request.parsed_url.scheme)
    
    @classmethod
    def create_conn_from_url(cls,url: str):
        _request = Request("",url)
        return cls.from_request(request=_request)
    

    async def connect(self, timeout: float = 10.0):
        self._loop = asyncio.get_event_loop()

        try:
            infos = await self._loop.getaddrinfo(
                self.host, self.port,
                type=socket.SOCK_STREAM,
            )
        except socket.gaierror as e:
            raise DNSError(f"Cannot resolve '{self.host}': {e}")

        if not infos:
            raise DNSError(f"No addresses found for '{self.host}'")

        family, socktype, proto, canonname, sockaddr = infos[0]

       
        if self.schema == "https":
            context = ssl.create_default_context()
            transport, self.protocol = await self._loop.create_connection(
                lambda: MyProtocol(),
                host=self.host,
                port=self.port,
                family=family,
                proto=proto,
                
            )

            self.tls_transport = await self._loop.start_tls(
                
                transport=transport,
                protocol=self.protocol,
                sslcontext=context
            )

        else:
            self._sock = socket.socket(family, socktype, proto)
            self._sock.setblocking(False)

            try:
                await asyncio.wait_for(
                    self._loop.sock_connect(self._sock, sockaddr),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                self.close()
                raise TimeoutError(f"Connect to '{self.host}:{self.port}' timed out")
            except OSError as e:
                self.close()
                raise ConnectError(f"Cannot connect to '{self.host}:{self.port}': {e}")

    async def send(self, data: bytes):
        if self.schema == "https":
            self.tls_transport.write(data)
        else:
            await self._loop.sock_sendall(self._sock, data)

    async def recv(self, n: int = 4096) -> bytes:
        if self.schema == "https":
            return await self.protocol.read()
        else:
            return await self._loop.sock_recv(self._sock, n)

    def close(self):
        if self.schema == "https" and self.tls_transport:
            self.tls_transport.close()
        elif self._sock:
            self._sock.close()
            self._sock = None

    @property
    def is_connected(self) -> bool:
        return self._sock is not None or self.tls_transport is not None
    


class MyProtocol(asyncio.Protocol):

    def __init__(self):
        super().__init__()
        self.queue = asyncio.Queue()

    def data_received(self, data):
        self.queue.put_nowait(data)
        return super().data_received(data)
    
    async def read(self):
        return await self.queue.get()
    
    
