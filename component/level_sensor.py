import logging
from enum import Enum
from typing import Optional


logger = logging.getLogger('aquarium.level_sensor')


class LevelSensorMode(Enum):
    dry = 'dry'
    variable = 'variable'
    wet = 'wet'


class LevelSensorStatus(Enum):
    dry = 'dry'
    wet = 'wet'


class LevelSensor:

    id: Optional[str] = None
    mode: Optional[LevelSensorMode] = None
    resource_key: Optional[str] = None
    level: Optional[int] = None

    def __init__(self, _id: str, _level: int, _mode: str, _resource_key: str):
        self.id = _id
        self.level = _level
        self.mode = LevelSensorMode[_mode]
        self.resource_key = _resource_key

    def water_presence(self) -> LevelSensorStatus:
        # logger.info(f'Checking for water presence on level sensor: {self.to_string()}')
        if self.mode != LevelSensorMode.dry:
            return LevelSensorStatus.wet
        return LevelSensorStatus.dry

    def to_string(self):
        return f'LevelSensor(id: {self.id}, level: {self.level}, mode: {self.mode}, resource_key: {self.resource_key})'
