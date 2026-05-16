import asyncio

from aiorequests import Client

async def main():


    client = Client()

    async with client as session:
        response = await session.get("https://httpbin.org/get")



    print(response.body)


asyncio.run(main())
