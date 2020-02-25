import asyncio
import inspect
import json
import ssl
from datetime import datetime

import certifi
import slacker
import websockets


class BaseBot:
    def __init__(self, bot_slack, user_slack):
        self.bot_slack = bot_slack
        self.user_slack = user_slack
        self.channel = None
        self._socket = None
        self._set_command_info()

        self._load_from_file()

    def _set_command_info(self):
        self.command_dict = {function_name: getattr(self, function_name) for function_name in dir(self)
                             if callable(getattr(self, function_name)) and not function_name.startswith("_")}
        self.parameter_dict = {name: [i for i in inspect.signature(function).parameters.keys() if i not in ["self"]] for
                               name, function in self.command_dict.items()}
        self.help_dict = {function_name: f"!{function_name}{''.join([' ' + i for i in args])}" for function_name, args
                          in self.parameter_dict.items()}

    async def _listen(self):
        ssl_context = ssl.create_default_context()
        ssl_context.load_verify_locations(certifi.where())

        rtm_response = self.bot_slack.rtm.start()
        url = rtm_response.body['url']
        self._socket = await websockets.connect(url, ssl=ssl_context)

        response = ""

        while True:

            try:
                message = await self._receive_slack_message()

                if message:
                    response = await self._run(message)

            except Exception as e:
                response = self._exception_handle_and_return_message(e)

            if response and self.channel:
                self._send_slack_message(response)
                response = ""

    async def _receive_slack_message(self):

        while True:
            json_message = json.loads(await self._socket.recv())
            if json_message.get("type") == "message" and 'bot_id' not in json_message:
                message = json_message.get("text")
                self.channel = json_message.get("channel")
                return message
            await asyncio.sleep(0.05)

    def _send_slack_message(self, message):
        try:
            self.user_slack.chat.post_message(self.channel, message[:10000])
        except slacker.Error as e:
            self.bot_slack.chat.post_message(self.channel, message[:10000])

    @staticmethod
    def _exception_handle_and_return_message(exception):
        if exception is TypeError:
            error_message = str(exception)
            if "positional" in error_message:
                message = "명령어의 인자 갯수가 맞지 않습니다. 하나의 인자 내 문자열의 띄어쓰기는 _ 로 대신 사용해주세요."
            elif "int()":
                message = "날짜는 숫자로만 입력해주세요."

        else:
            message = "error: " + str(exception)

        return message

    async def _run(self, command):
        if not command.startswith("!"):
            return
        command, *params = command[1:].split(" ")
        for i in range(len(params)):
            params[i] = params[i].replace("\"", "").replace("\'", "").replace("_", " ")

        if command not in self.command_dict:
            return "잘못된 명령어 입니다. \"!명령어\"를 입력하시면 명령어 목록을 표시합니다."

        function = self.command_dict[command]

        if asyncio.iscoroutinefunction(function):
            return await function(*params)
        else:
            return function(*params)

    def _load_from_file(self):
        raise NotImplementedError()

    def _write_to_file(self):
        raise NotImplementedError()

    @classmethod
    def _slack_format_korean(cls, string, reserve, left_align=True):

        reserve = reserve * 3
        korean_count = 0

        for character in string:
            if cls._is_korean(character):
                korean_count += 1

        space = reserve - korean_count * 2 - len(string)

        return " " * space * (not left_align) + string + " " * space * left_align

    def _get_bot_message_timestamps(self, limit):
        timestamps = []
        try:
            response = self.user_slack.conversations.history(self.channel, limit=limit)
        except slacker.Error:
            response = self.bot_slack.conversations.history(self.channel, limit=limit)

        if response.successful:
            json_response = json.loads(response.raw)
            messages = json_response['messages']

            for message in messages:
                if "bot_id" in message and message['username'] == 'D-Day':
                    timestamps.append(message['ts'])

        return timestamps

    def clear(self, limit=30):
        for timestamp in self._get_bot_message_timestamps(limit):
            try:
                self.user_slack.chat.delete(self.channel, timestamp)
            except slacker.Error:
                self.bot_slack.chat.delete(self.channel, timestamp)

    @staticmethod
    def _is_korean(character):
        return ord('가') < ord(character) < ord('힇')

    @staticmethod
    def _to_json(obj):
        return json.dumps(obj, default=lambda x: x.isoformat(' ', 'seconds') if type(x) == datetime else x.__dict__,
                          sort_keys=True, indent=4)
