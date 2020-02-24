import asyncio

from slacker import Slacker

from DDayBot import DDayBot

json_file_name = "jsonData.json";


async def main():
    token = ""
    slack = Slacker(token)

    bot = DDayBot(slack)
    await bot._listen()


if __name__ == '__main__':
    asyncio.run(main())
