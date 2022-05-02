from enum import Enum
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
        # Todo: Set status based on actual float switch

    def get_status(self) -> FloatSwitchStatus:
        # Todo: Change this to get status from actual float switch
        if self.mode != FloatSwitchMode.dry:
            return FloatSwitchStatus.wet
        return FloatSwitchStatus.dry

    def to_string(self):
        return f'FloatSwitch(id: {self.id}, level: {self.level}, mode: {self.mode}, resource_key: {self.resource_key}, resource_type: {self.resource_type})'
