from connection import Connection
import asyncio
from request import Request

async def main():
    connection = Connection("httpbin.org",80)

    await connection.connect()
    print(f"Connected: {connection.is_connected}")

    request = Request("get","httpbin.org/get")

    await connection.send(
        request.to_bytes() 
    )
    response = b''
    while chunk := await connection.recv():
        response += chunk

    print(str(response.decode()))
    connection.close

asyncio.run(main())