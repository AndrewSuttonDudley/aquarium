import logging

from component import LevelSensor
from component import LevelSensorMode


logger = logging.getLogger('aquarium.level_sensor_service')


def get_water_level(_level_sensors: list[LevelSensor]) -> int:
    _max_level: int = 0
    for _level_sensor in _level_sensors:
        if _level_sensor.water_presence() and _level_sensor.level > _max_level:
            _max_level = _level_sensor.level
    return _max_level


def safety_check(_level_sensors: list[LevelSensor]) -> bool:
    logger.info(f'Starting safety check on level sensors')
    for _level_sensor in _level_sensors:
        _water_presence = _level_sensor.water_presence()
        if _level_sensor.mode.value != LevelSensorMode.variable.value and _water_presence.value != _level_sensor.mode.value:
            return False
    return True
