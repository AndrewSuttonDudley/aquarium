from typing import Optional

from component import Schedule


class Aquarium:

    id: Optional[str] = None
    capacity: Optional[int] = None
    host: Optional[str] = None
    initialized: bool = False
    name: Optional[str] = None
    registered: bool = False
    schedules: Optional[list[Schedule]] = None

    def __init__(self, id: str, capacity: int, host: str, name: str):
        self.id = id
        self.capacity = capacity
        self.host = host
        self.initialized = True
        self.name = name
        self.schedules = list()

    def to_string(self):
        return f'Aquarium(id: {self.id}, capacity: {self.capacity}, host: {self.host}, name: {self.name})'
