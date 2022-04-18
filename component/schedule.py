from typing import Optional


class Schedule:

    id: Optional[str] = None
    day_of_week: Optional[str] = None
    hour: Optional[str] = None
    minute: Optional[str] = None
    percent_change: Optional[int] = None
    type: Optional[str] = None

    def __init__(self, id: str, day_of_week: str, hour: str, minute: str, percent_change: str, type: str):
        self.id = id
        self.day_of_week = day_of_week
        self.hour = hour
        self.minute = minute
        self.percent_change = percent_change
        self.type = type

    def to_string(self):
        return f'Schedule(id: {self.id}, type: {self.type}, percent_change: {self.percent_change}, ' \
               f'day_of_week: {self.day_of_week}, time: {self.hour}:{self.minute})'
