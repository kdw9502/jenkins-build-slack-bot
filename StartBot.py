import asyncio

from slacker import Slacker

from DDayBot import DDayBot


async def main():
    bot_token = ""
    bot_slack = Slacker(bot_token)

    user_token = ""
    user_slack = Slacker(user_token)

    bot = DDayBot(bot_slack, user_slack)
    await bot._listen()


if __name__ == '__main__':
    asyncio.run(main())
