from __future__ import annotations

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


    async def _request(self,method: str,url:str,body: None | str | dict = None, headers: dict[str,str] | None = None, n:int = 4096):

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
        
    async def get(self,url:str, headers: dict[str,str] | None = None, n:int = 4096):
        return await self._request("get", url, headers=headers, n=n)
    

    async def post(self,url:str,body: None | str | dict = None, headers: dict[str,str] | None = None, n:int = 4096):
        return await self._request("post",url,body,headers,n)
    

    async def put(self,url:str,body: None | str | dict = None, headers: dict[str,str] | None = None, n:int = 4096):
        return await self._request("put",url,body,headers,n)
    

    async def patch(self,url:str,body: None | str | dict = None, headers: dict[str,str] | None = None, n:int = 4096):
        return await self._request("patch",url,body,headers,n)
    

    async def delete(self,url:str,body: None | str | dict = None, headers: dict[str,str] | None = None, n:int = 4096):
        return await self._request("delete",url,body,headers,n)
    

    def close_all_conn(self):
        for conn in self.connections.values():
            conn.close()
    

    
    
