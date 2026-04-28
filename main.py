from connection import Connection
import asyncio
from request import Request

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

    print(str(response.decode()))
    connection.close()

asyncio.run(main())