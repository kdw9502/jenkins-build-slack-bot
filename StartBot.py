import asyncio

from slacker import Slacker
import argparse
from JenkinsBuildBot import JenkinsBuildBot


async def main():
    parser = argparse.ArgumentParser(description="Simple jenkins build invoke bot")

    parser.add_argument('bot_token',help='Bot User OAuth Access Token')
    parser.add_argument('user_token', help='OAuth Access Token')

    args = parser.parse_args()

    bot_slack = Slacker(args.bot_token)
    user_slack = Slacker(args.user_token)

    bot = JenkinsBuildBot(bot_slack, user_slack)
    await bot._listen()


if __name__ == '__main__':
    asyncio.run(main())
