from apscheduler.schedulers.background import BackgroundScheduler
from enum import Enum
import RPi.GPIO as GPIO
import logging
from typing import Optional
import os

from component.heater import Heater
from component.float_switch import FloatSwitch
from component.level_sensor import LevelSensor
from service import level_sensor_service
from component.pump import Pump
from connector import system_connector
from component.thermometer import Thermometer
from component.water_jet import WaterJet
from util import file_util


logger = logging.getLogger('aquarium.aquarium_service')


class AquariumJob(Enum):
    register = 'register'
    health_check = 'health_check'
    safety_check = 'safety_check'


class AquariumStatus(Enum):
    started = 'started'
    initializing = 'initializing'
    registering = 'registering'
    active = 'active'


id: Optional[str] = None
capacity: Optional[int] = None
description: Optional[str] = None
filter_pumps = []
heaters = []
level_sensor: Optional[LevelSensor] = None
name: Optional[str] = None
pid: Optional[int] = None
port: Optional[int] = None
scheduler: Optional[BackgroundScheduler] = None
status = AquariumStatus.started
system_host: Optional[str] = None
thermometers = []
water_jets = []


def change_status(new_status: AquariumStatus):
    global status
    logger.info(f'Changing aquarium status from {status} to {new_status}')
    match status:
        case AquariumStatus.active:
            logger.info('status: ACTIVE')
            match new_status:
                case AquariumStatus.registering:
                    logger.info('new_status: REGISTERING')
                    status = AquariumStatus.registering
                    scheduler.remove_job(job_id=AquariumJob.health_check.value)
                    scheduler.add_job(func=lambda: system_connector.register_aquarium_with_system(id), id=AquariumJob.register.value,
                                      trigger='interval', seconds=10)
                case _:
                    logger.info(f'Invalid status change from {status} to {new_status}')

        case AquariumStatus.initializing:
            logger.info('status: INITIALIZING')
            match new_status:
                case AquariumStatus.registering:
                    logger.info('new_status: REGISTERING')
                    status = AquariumStatus.registering
                    scheduler.add_job(func=lambda: system_connector.register_aquarium_with_system(id), id=AquariumJob.register.value,
                                      trigger='interval', seconds=10)
                case _:
                    logger.info(f'Invalid status change from {status} to {new_status}')

        case AquariumStatus.registering:
            logger.info('status: REGISTERING')
            match new_status:
                case AquariumStatus.active:
                    logger.info('new_status: ACTIVE')
                    status = AquariumStatus.active
                    scheduler.remove_job(job_id=AquariumJob.register.value)
                    scheduler.add_job(func=lambda: system_connector.aquarium_health_check(id), id=AquariumJob.health_check.value,
                                      trigger='interval', seconds=10)
                case _:
                    logger.info(f'Invalid status change from {status} to {new_status}')

        case AquariumStatus.started:
            logger.info('status: STARTED')
            match new_status:
                case AquariumStatus.initializing:
                    logger.info('new_status: INITIALIZING')
                    status = AquariumStatus.initializing
                case _:
                    logger.info(f'Invalid status change from {status} to {new_status}')

        case _:
            logger.info(f'status value not recognized: {status}')


def initialize(config_filename: str, _scheduler: BackgroundScheduler):
    global id, capacity, description, name, pid, port, scheduler, status, system_host
    status = AquariumStatus.initializing
    logger.info('Initializing AquariumService')
    GPIO.setmode(GPIO.BCM)
    aquarium_config = file_util.load_json_file(config_filename)

    initialize_components(aquarium_config)

    id = aquarium_config['id']
    capacity = aquarium_config['capacity']
    description = aquarium_config['description']
    name = aquarium_config['name']
    pid = os.getpid()
    port = aquarium_config['port']
    scheduler = _scheduler
    system_host = aquarium_config['systemHost']

    scheduler.add_job(func=safety_check, id=AquariumJob.safety_check.value, trigger='interval', seconds=10)
    change_status(AquariumStatus.registering)


def initialize_components(aquarium_config):
    initialize_filter_pumps(aquarium_config)
    initialize_heaters(aquarium_config)
    initialize_level_sensor(aquarium_config)
    initialize_thermometers(aquarium_config)
    initialize_water_jets(aquarium_config)


def initialize_filter_pumps(aquarium_config):
    logger.info('In AquariumService::initialize_filter_pumps')
    for filter_pump in aquarium_config['filterPumps']:
        logger.info(f'Initializing source pump id: {filter_pump["id"]}')
        filter_pumps.append(Pump(filter_pump['id'], filter_pump['resourceKey'], filter_pump['resourceType']))
    logger.info(f'{len(filter_pumps)} filter pumps initialized')


def initialize_heaters(aquarium_config):
    logger.info('In AquariumService::initialize_heaters')
    for heater in aquarium_config['heaters']:
        logger.info(f'Initializing heater id: {heater["id"]}')
        heaters.append(Heater(heater['id'], heater['resourceKey'], heater['resourceType']))
    logger.info(f'{len(heaters)} heaters initialized')


def initialize_level_sensor(aquarium_config):
    global level_sensor
    logger.info('In AquariumService::initialize_level_sensor')
    level_sensor = LevelSensor(aquarium_config['levelSensor']['id'])

    for _float_switch in aquarium_config['levelSensor']['floatSwitches']:
        logger.info(f'Initializing float switch id: {_float_switch["id"]}')
        level_sensor.add_float_switch(FloatSwitch(_float_switch['id'], _float_switch['level'], _float_switch['mode'], _float_switch['resourceKey'], _float_switch['resourceType']))
    logger.info(f'Level sensor initialized with {len(level_sensor.float_switches)} float switches')


def initialize_thermometers(aquarium_config):
    logger.info('In AquariumService::initialize_thermometers')
    for thermometer in aquarium_config['thermometers']:
        logger.info(f'Initializing thermometer id: {thermometer["id"]}')
        thermometers.append(Thermometer(thermometer['id'], thermometer['resourceKey'], thermometer['resourceType']))
    logger.info(f'{len(thermometers)} thermometers initialized')


def initialize_water_jets(aquarium_config):
    logger.info('In AquariumService::initialize_water_jets')
    for water_jet in aquarium_config['waterJets']:
        logger.info(f'Initializing water jet id: {water_jet["id"]}')
        water_jets.append(WaterJet(water_jet['id'], water_jet['resourceKey'], water_jet['resourceType']))
    logger.info(f'{len(water_jets)} water jets initialized')


def level_check() -> int:
    logger.info('Checking water level')
    return 100


def safety_check():
    logger.info('Starting safety check')
    _safe_levels: bool = level_sensor_service.safety_check(level_sensor)

    if not _safe_levels:
        logger.info('Water level safety check failed. Server exiting')
        os.kill(pid, 9)

    logger.info('Safety checks passed')
