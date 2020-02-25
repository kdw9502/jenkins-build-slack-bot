# -*- coding: utf-8 -*-
import asyncio
import inspect
import json
import os
import ssl
from datetime import datetime
import slacker

import certifi
import websockets

from Event import Event

json_file_name = "jsonData.json"


# noinspection PyPep8Naming,NonAsciiCharacters
class DDayBot:
    def __init__(self, bot_slack, user_slack):

        self.command_dict = {function_name: getattr(DDayBot, function_name) for function_name in dir(self)
                             if callable(getattr(DDayBot, function_name)) and not function_name.startswith("_")}
        self.parameter_dict = {name: [i for i in inspect.signature(function).parameters.keys() if i not in ["self"]] for
                               name, function in self.command_dict.items()}
        self.help_dict = {function_name: f"!{function_name}{''.join([' ' + i for i in args])}" for function_name, args
                          in self.parameter_dict.items()}
        self.bot_slack = bot_slack
        self.user_slack = user_slack
        self.channel = None

        self._load_from_file()

    async def _listen(self):
        ssl_context = ssl.create_default_context()
        ssl_context.load_verify_locations(certifi.where())

        rtm_response = self.bot_slack.rtm.start()
        url = rtm_response.body['url']
        socket = await websockets.connect(url, ssl=ssl_context)

        response = ""

        while True:
            await asyncio.sleep(0.1)

            json_message = json.loads(await socket.recv())

            try:
                if json_message.get("type") == "message":
                    message = json_message.get("text")
                    self.channel = json_message.get("channel")

                    if message:
                        response = self._run(message)
            except TypeError as type_error:
                error_message = str(type_error)
                if "positional" in error_message:
                    response = "명령어의 인자 갯수가 맞지 않습니다. 띄어쓰기는 _ 로 대신 사용해주세요."
                elif "int()":
                    response = "날짜는 숫자로만 입력해주세요."

                response += str(type_error)
                # raise type_error

            except Exception as e:
                response = "error: " + str(e)
                raise e

            if response and self.channel:
                self.user_slack.chat.post_message(self.channel, response)

    def _run(self, command):
        if not command.startswith("!"):
            return
        command, *params = command[1:].split(" ")
        for i in range(len(params)):
            params[i] = params[i].replace("\"", "").replace("\'", "").replace("_", " ")

        if command not in self.command_dict:
            return "잘못된 명령어 입니다. \"!명령어\"를 입력하시면 명령어 목록을 표시합니다."

        return self.command_dict[command](self, *params)

    def _write_to_file(self):
        with open(json_file_name, "w+") as file:
            file.write(ToJson(self.events))
            file.truncate()

    def _load_from_file(self):
        if os.path.exists(json_file_name):
            with open(json_file_name, "r") as file:
                contents = file.read()
                if contents:
                    json_value = json.loads(contents)
                    self.events = Event.fromJson(json_value)
                else:
                    self.events = []

    def 명령어(self):
        return "\n".join(["명령어 목록"] + list(self.help_dict.values()))

    def 등록(self, 이벤트이름, 년, 월, 일, 시=0, 분=0):
        if int(년) < 100:
            년 = int(년) + 2000

        self.삭제(이벤트이름)
        self.events.append(Event(이벤트이름, datetime(int(년), int(월), int(일), int(시), int(분))))
        self._write_to_file()
        return f"{이벤트이름}이 등록되었습니다."

    def 목록(self):
        event_strings = []

        events = sorted(self.events, key=lambda x: x.date)

        for event in events:
            format_name = DDayBot._slack_format_korean(event.name, 15)

            event_strings.append(f"{format_name} {event.date.isoformat(' ', 'minutes')} D{-event.remainDayFromNow()}")

        if len(event_strings) == 0:
            return "이벤트가 없습니다."

        return "\n".join(event_strings)

    @staticmethod
    def _slack_format_korean(string, reserve, left_align=True):

        reserve = reserve * 3
        korean_count = 0

        for character in string:
            if is_korean(character):
                korean_count += 1

        space = reserve - korean_count * 2 - len(string)

        return " " * space * (not left_align) + string + " " * space * left_align

    def 삭제(self, 이벤트이름):
        for event in self.events:
            if event.name == 이벤트이름:
                self.events.remove(event)
                self._write_to_file()
                break
        return f"{이벤트이름}이 삭제되었습니다."

    def _get_bot_message_timestamps(self):
        timestamps = []
        response = self.user_slack.conversations.history(self.channel, limit=30)

        if response.successful:
            json_response = json.loads(response.raw)
            messages = json_response['messages']

            for message in messages:
                if "bot_id" in message and message['username'] == 'D-Day':
                    timestamps.append(message['ts'])

        return timestamps

    def clear(self):
        for timestamp in self._get_bot_message_timestamps():
            try:
                self.user_slack.chat.delete(self.channel, timestamp)
            except slacker.Error:
                self.bot_slack.chat.delete(self.channel, timestamp)


def is_korean(character):
    return ord('가') < ord(character) < ord('힇')


def ToJson(obj):
    return json.dumps(obj, default=lambda x: x.isoformat(' ', 'seconds') if type(x) == datetime else x.__dict__,
                      sort_keys=True, indent=4)
