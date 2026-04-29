from connection import Connection
import asyncio
from request import Request
from response import Response
from client import Client

async def main():


    client = Client()

    async with client as session:
        response = await session.get("http://httpbin.org/get")



    print(response.body)


asyncio.run(main())