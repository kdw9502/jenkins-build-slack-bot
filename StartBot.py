import argparse
import asyncio
import traceback

from slacker import Slacker

from JenkinsBuildBot import JenkinsBuildBot


async def main():
    parser = argparse.ArgumentParser(description="Simple jenkins build invoke bot")

    parser.add_argument('bot_token', help='Bot User OAuth Access Token')
    parser.add_argument('user_token', help='OAuth Access Token')
    parser.add_argument('jenkins_url', help='jenkins server url')

    args = parser.parse_args()

    bot_slack = Slacker(args.bot_token)
    user_slack = Slacker(args.user_token)

    bot = JenkinsBuildBot(bot_slack, user_slack, args.jenkins_url)
    while True:
        try:
            await bot._listen()
        except:
            traceback.print_exc()
            await asyncio.sleep(60)


if __name__ == '__main__':
    asyncio.run(main())
