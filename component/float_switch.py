from enum import Enum
from RPi import GPIO
from typing import Optional

from component.resource_type import ResourceType


class FloatSwitchMode(Enum):
    dry = 'dry'
    variable = 'variable'
    wet = 'wet'


class FloatSwitchStatus(Enum):
    dry = 'dry'
    wet = 'wet'


class FloatSwitch:

    id: Optional[str] = None
    level: Optional[int] = None
    mode: Optional[FloatSwitchMode] = None
    resource_key: Optional[int] = None
    resource_type: Optional[ResourceType] = None

    def __init__(self, id: str, level: int, mode: FloatSwitchMode, resource_key: int, resource_type: ResourceType):
        self.id = id
        self.level = level
        self.mode = mode
        self.resource_key = resource_key
        self.resource_type = resource_type

        GPIO.setup(self.resource_key, GPIO.IN)

    def get_status(self) -> FloatSwitchStatus:
        if GPIO.input(self.resource_key) == 1:
            return FloatSwitchStatus.dry
        else:
            return FloatSwitchStatus.wet

    def to_string(self):
        return f'FloatSwitch(id: {self.id}, level: {self.level}, mode: {self.mode}, resource_key: {self.resource_key}, resource_type: {self.resource_type})'
