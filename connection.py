import asyncio
import socket
from request import Request


from exception import ConnectError, DNSError, TimeoutError


class Connection:
    def __init__(self, host: str, port: int):
        self.host: str = host
        self.port: int  = port
        self._sock: socket.socket | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
    
    @classmethod
    def from_request(cls,request:Request):
        return cls(request.parsed_url.hostname,request.port)
    

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
        await self._loop.sock_sendall(self._sock, data)

    async def recv(self, n: int = 4096) -> bytes:
        return await self._loop.sock_recv(self._sock, n)

    def close(self):
        if self._sock:
            self._sock.close()
            self._sock = None

    @property
    def is_connected(self) -> bool:
        return self._sock is not None