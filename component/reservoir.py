from typing import Optional


class Reservoir:

    id: Optional[str] = None
    capacity: Optional[int] = None
    host: Optional[str] = None
    initialized: bool = True
    name: Optional[str] = None
    registered: bool = False
    schedules: Optional[list] = None
    tested: bool = False

    def __init__(self, id, capacity, host, name):
        self.id = id
        self.capacity = capacity
        self.host = host
        self.name = name
        self.schedules = list()

    def to_string(self):
        return f'Reservoir(id: {self.id}, capacity: {self.capacity}, name: {self.name})'
