# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime

from BaseBot import BaseBot
from Event import Event


# noinspection PyPep8Naming,NonAsciiCharacters
class DDayBot(BaseBot):
    def __init__(self, bot_slack, user_slack):
        self.json_file_name = "ddaybot.json"

        BaseBot.__init__(self, bot_slack, user_slack)

    def _write_to_file(self):
        with open(self.json_file_name, "w+") as file:
            file.write(self.ToJson(self.events))
            file.truncate()

    def _load_from_file(self):
        if os.path.exists(self.json_file_name):
            with open(self.json_file_name, "r") as file:
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

    def 삭제(self, 이벤트이름):
        for event in self.events:
            if event.name == 이벤트이름:
                self.events.remove(event)
                self._write_to_file()
                break
        return f"{이벤트이름}이 삭제되었습니다."