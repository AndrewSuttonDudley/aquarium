from enum import Enum
import logging
from typing import Optional

from component import FloatSwitch
from component import FloatSwitchStatus


logger = logging.getLogger('aquarium.level_sensor')


class LevelSensorMode(Enum):
    dry = 'dry'
    variable = 'variable'
    wet = 'wet'


class LevelSensorStatus(Enum):
    dry = 'dry'
    error = 'error'
    wet = 'wet'


class LevelSensor:

    id: Optional[str] = None
    float_switches: Optional[list[FloatSwitch]] = None

    def __init__(self, _id):
        self.id = _id
        self.float_switches = []

    def add_float_switch(self, float_switch: FloatSwitch):
        self.float_switches.append(float_switch)

    def get_current_level(self) -> int:
        highest_wet_float_switch: Optional[FloatSwitch] = None
        for float_switch in self.float_switches:
            if highest_wet_float_switch is None or \
                    (float_switch.get_status() == FloatSwitchStatus.wet and highest_wet_float_switch.level < float_switch.level):
                highest_wet_float_switch = float_switch
        return highest_wet_float_switch.level

    def to_string(self):
        return f'LevelSensor(id: {self.id})'
