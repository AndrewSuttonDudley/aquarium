import logging

from component import LevelSensor
from component import LevelSensorMode


logger = logging.getLogger('aquarium.level_sensor_service')


def get_water_level(_level_sensor: LevelSensor) -> int:
    _max_level: int = 0
    for _float_switch in _level_sensor.float_switches:
        if _float_switch.water_presence() and _float_switch.level > _max_level:
            _max_level = _float_switch.level
    return _max_level


def safety_check(_level_sensor: LevelSensor) -> bool:
    logger.info(f'Starting safety check on level sensor')
    for _float_switch in _level_sensor.float_switches:
        _water_presence = _float_switch.water_presence()
        if _float_switch.mode.value != LevelSensorMode.variable.value and _water_presence.value != _float_switch.mode.value:
            return False
    return True
