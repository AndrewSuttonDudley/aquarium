from apscheduler.schedulers.background import BackgroundScheduler
from enum import Enum
import logging
from typing import Optional
import requests

from component.heater import Heater
from component.level_sensor import LevelSensor
from component.pump import Pump
from component.thermometer import Thermometer
from component.water_jet import WaterJet
from util import file_util


logger = logging.getLogger('aquarium.aquarium_service')


class AquariumJob(Enum):
    REGISTER = 'register'


class AquariumStatus(Enum):
    STARTED = 'started'
    INITIALIZING = 'initializing'
    REGISTERING = 'registering'
    ACTIVE = 'active'


id: Optional[str] = None
capacity: Optional[int] = None
description: Optional[str] = None
filter_pumps = []
heaters = []
level_sensors = []
name: Optional[str] = None
port: Optional[int] = None
scheduler: Optional[BackgroundScheduler] = None
status = AquariumStatus.STARTED
system_host: Optional[str] = None
thermometers = []
water_jets = []


def initialize(config_filename: str, _scheduler: BackgroundScheduler):
    global id, capacity, description, name, port, scheduler, status, system_host
    status = AquariumStatus.INITIALIZING
    logger.info('Initializing AquariumService')
    aquarium_config = file_util.load_json_file(config_filename)

    initialize_components(aquarium_config)

    id = aquarium_config['id']
    capacity = aquarium_config['capacity']
    description = aquarium_config['description']
    name = aquarium_config['name']
    port = aquarium_config['port']
    scheduler = _scheduler
    system_host = aquarium_config['systemHost']

    scheduler.add_job(func=register_with_system, id=AquariumJob.REGISTER.value, trigger='interval', seconds=6)
    status = AquariumStatus.REGISTERING


def initialize_components(aquarium_config):
    initialize_filter_pumps(aquarium_config)
    initialize_heaters(aquarium_config)
    initialize_level_sensors(aquarium_config)
    initialize_thermometers(aquarium_config)
    initialize_water_jets(aquarium_config)


def initialize_filter_pumps(aquarium_config):
    logger.info('In AquariumService::initialize_filter_pumps')
    for filter_pump in aquarium_config['filterPumps']:
        logger.info(f'Initializing source pump id: {filter_pump["id"]}')
        filter_pumps.append(Pump(filter_pump['id'], filter_pump['resourceKey']))
    logger.info(f'{len(filter_pumps)} filter pumps initialized')


def initialize_heaters(aquarium_config):
    logger.info('In AquariumService::initialize_heaters')
    for heater in aquarium_config['heaters']:
        logger.info(f'Initializing heater id: {heater["id"]}')
        heaters.append(Heater(heater['id'], heater['resourceKey']))
    logger.info(f'{len(heaters)} heaters initialized')


def initialize_level_sensors(aquarium_config):
    logger.info('In AquariumService::initialize_level_sensors')
    for level_sensor in aquarium_config['levelSensors']:
        logger.info(f'Initializing level sensor id: {level_sensor["id"]}')
        level_sensors.append(LevelSensor(level_sensor['id'], level_sensor['resourceKey']))
    logger.info(f'{len(level_sensors)} level sensors initialized')


def initialize_thermometers(aquarium_config):
    logger.info('In AquariumService::initialize_thermometers')
    for thermometer in aquarium_config['thermometers']:
        logger.info(f'Initializing thermometer id: {thermometer["id"]}')
        thermometers.append(Thermometer(thermometer['id'], thermometer['resourceKey']))
    logger.info(f'{len(thermometers)} thermometers initialized')


def initialize_water_jets(aquarium_config):
    logger.info('In AquariumService::initialize_water_jets')
    for water_jet in aquarium_config['waterJets']:
        logger.info(f'Initializing water jet id: {water_jet["id"]}')
        water_jets.append(WaterJet(water_jet['id'], water_jet['resourceKey']))
    logger.info(f'{len(water_jets)} water jets initialized')


def register_with_system():
    global status
    url = f'{system_host}/aquariums/{id}/register'
    logger.info(f'Attempting to register with System url: {url}')
    try:
        response = requests.put(url)
    except OSError:
        logger.info(f'Connection refused. System not found.')
    else:
        logger.info(f'Success: {response}')
        scheduler.remove_job(job_id=AquariumJob.REGISTER.value)
        status = AquariumStatus.ACTIVE
