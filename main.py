from connection import Connection
import asyncio


async def main():
    connection = Connection("httpbin.org",80)

    await connection.connect()
    print(f"Connected: {connection.is_connected}")

    await connection.send(
        b"GET /get HTTP/1.1\r\n"
        b"Host: httpbin.org\r\n"
        b"Connection: close\r\n"
        b"\r\n"
    )
    response = b''
    while chunk := await connection.recv():
        response += chunk

    print(str(response.decode()))
    connection.close

asyncio.run(main())