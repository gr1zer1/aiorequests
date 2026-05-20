from __future__ import annotations

import asyncio

from aiorequests.errors.exception import AsyncHttpError
from aiorequests.http.request import Request
from aiorequests.http.response import Response
from aiorequests.transport.connection import Connection

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client

class Session:
    def __init__(self, client: Client):
        self.client = client
        self.connections: dict[str, Connection] = {}
    

    def build_url(self, url: str, params: dict[str, str] | None = None) -> str:
        if params:
            query_string = "&".join(f"{k}={v}" for k, v in params.items())
            url += f"?{query_string}"
        return url


    async def _send_once(self,method: str,url:str,body: None | str | dict = None, headers: dict[str,str] | None = None, n:int = 4096):
        
        connection = self.connections.get(url)
        if connection == None:
            connection = Connection.create_conn_from_url(url)
            self.connections[url] = connection
            await connection.connect()

        new_headers = {**(self.client.headers or {}),**(headers or {})}
            
        request = Request(method,url,new_headers,body)

        await connection.send(request.to_bytes())

        buffer = b''
        while b"\r\n\r\n" not in buffer:
            buffer += await connection.recv(n)
        
        head,rest = buffer.split(b"\r\n\r\n", 1)


        content_length:int = 0
        heads = head.split(b"\r\n")
        for h in heads:
            if b"Content-Length" in h:
                _,content_length = h.decode().split(":",1)
        
        body = rest

        while len(body) < int(content_length):
            body += await connection.recv(n)

        response = Response.from_bytes(head+b"\r\n\r\n"+body)
        
        return response

    def _drop_connection(self, url: str):
        connection = self.connections.pop(url, None)
        if connection is not None:
            connection.close()

    async def _request(
        self,
        method: str,
        url: str,
        body: None | str | dict = None,
        headers: dict[str, str] | None = None,
        n: int = 4096,
        retries: int = 0,
        retry_delay: float = 0.0,
        retry_statuses: tuple[int, ...] = (500, 502, 503, 504),
    ):
        if retries < 0:
            raise ValueError("retries must be greater than or equal to 0")

        last_attempt = retries + 1

        for attempt in range(last_attempt):
            try:
                response = await self._send_once(method, url, body, headers, n)
            except (AsyncHttpError, OSError, EOFError):
                self._drop_connection(url)

                if attempt == retries:
                    raise

                if retry_delay > 0:
                    await asyncio.sleep(retry_delay)

                continue

            if response.status_code not in retry_statuses or attempt == retries:
                return response

            self._drop_connection(url)

            if retry_delay > 0:
                await asyncio.sleep(retry_delay)
        
    async def get(self,url:str, headers: dict[str,str] | None = None, n:int = 4096, retries: int = 0, retry_delay: float = 0.0):
        return await self._request("get", url, headers=headers, n=n, retries=retries, retry_delay=retry_delay)
    

    async def post(self,url:str,body: None | str | dict = None, headers: dict[str,str] | None = None, n:int = 4096, retries: int = 0, retry_delay: float = 0.0):
        return await self._request("post",url,body,headers,n,retries,retry_delay)
    

    async def put(self,url:str,body: None | str | dict = None, headers: dict[str,str] | None = None, n:int = 4096, retries: int = 0, retry_delay: float = 0.0):
        return await self._request("put",url,body,headers,n,retries,retry_delay)
    

    async def patch(self,url:str,body: None | str | dict = None, headers: dict[str,str] | None = None, n:int = 4096, retries: int = 0, retry_delay: float = 0.0):
        return await self._request("patch",url,body,headers,n,retries,retry_delay)
    

    async def delete(self,url:str,body: None | str | dict = None, headers: dict[str,str] | None = None, n:int = 4096, retries: int = 0, retry_delay: float = 0.0):
        return await self._request("delete",url,body,headers,n,retries,retry_delay)
    

    def close_all_conn(self):
        for conn in self.connections.values():
            conn.close()
    

    
    
