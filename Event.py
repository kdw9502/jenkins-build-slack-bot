from datetime import datetime


class Event:
    def __init__(self, name, date: datetime):
        self.name = name
        self.date = date

        self.owner = ""
        self.is_private = False

    def remainDayFromNow(self):

        target_year_month_day = datetime(self.date.year, self.date.month, self.date.day)
        now = datetime.now()
        now_year_month_day = datetime(now.year, now.month, now.day)

        deltaTime = target_year_month_day - now_year_month_day

        return deltaTime.days

    @classmethod
    def fromJson(cls, json):

        if type(json) is list:
            events = []
            for json_object in json:
                date = datetime.fromisoformat(json_object["date"])
                event = cls(json_object["name"], date)
                events.append(event)
            return events

        elif type(json) is dict:
            date = datetime.fromisoformat(json["date"])
            return cls(json["name"], date)
