from connection import Connection
import asyncio
from request import Request
from response import Response

async def main():
    request = Request("get","httpbin.org/get")
    connection = Connection.from_request(request)

    await connection.connect()
    print(f"Connected: {connection.is_connected}")


    await connection.send(
        request.to_bytes() 
    )
    response = b''
    while chunk := await connection.recv():
        response += chunk

    response = Response.from_bytes(response)
    print(response.body)

    connection.close()

asyncio.run(main())