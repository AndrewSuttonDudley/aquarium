from enum import Enum
from typing import Optional

from component import ResourceType


class HeaterStatus(Enum):
    off = 'off'
    on = 'on'


class Heater:

    id: Optional[str] = None
    resource_key: Optional[int] = None
    resource_type: Optional[ResourceType] = None
    status: Optional[HeaterStatus] = None

    def __init__(self, id: str, resource_key: int, resource_type: ResourceType):
        self.id = id
        self.resource_key = resource_key
        self.resource_type = resource_type
        # Todo: Turn heater off

    def print(self):
        print(f'Heater(id: {self.id}, resource_key: {self.resource_key}, resource_type: {self.resource_type})')

    def set_status(self, status: HeaterStatus):
        self.status = status
        # Todo: Change this to set the status of the actual heater
