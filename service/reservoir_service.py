from apscheduler.schedulers.background import BackgroundScheduler
from enum import Enum
from util import file_util
import logging
from typing import Optional
import os

from component.float_switch import FloatSwitch
from component.heater import Heater
from component.level_sensor import LevelSensor
from service import level_sensor_service
from component.pump import Pump
from connector import system_connector
from component.thermometer import Thermometer
from component.valve import Valve
from component.water_jet import WaterJet


logger = logging.getLogger('aquarium.reservoir_service')


class ReservoirJob(Enum):
    health_check = 'health_check'
    register = 'register'
    safety_check = 'safety_check'


class ReservoirStatus(Enum):
    started = 'started'
    initializing = 'initializing'
    registering = 'registering'
    active = 'active'


id: Optional[str] = None
capacity: Optional[int] = None
heaters = []
level_sensor: Optional[LevelSensor] = None
pid: Optional[int] = None
port: Optional[int] = None
receiver_pumps = []
receiver_valves = []
scheduler: Optional[BackgroundScheduler] = None
send_pumps = []
send_valves = []
source_pumps = []
source_valves = []
status = ReservoirStatus.started
system_host: Optional[str] = None
thermometers = []
water_jets = []
water_level: Optional[int] = None


def change_status(new_status: ReservoirStatus):
    global status
    logger.info(f'Changing reservoir status from {status} to {new_status}')
    match status:
        case ReservoirStatus.active:
            logger.info('status: ACTIVE')
            match new_status:
                case ReservoirStatus.registering:
                    logger.info('new_status: REGISTERING')
                    status = ReservoirStatus.registering
                    logger.info(f'Removing health check job with ID: {ReservoirJob.health_check.value}. Existing jobs:')
                    for job in scheduler.get_jobs():
                        logger.info(f'Job ID: {job.id}')
                    scheduler.remove_job(job_id=ReservoirJob.health_check.value)
                    scheduler.remove_job(job_id=ReservoirJob.safety_check.value)
                    scheduler.add_job(func=lambda: system_connector.register_reservoir_with_system(id),
                                      id=ReservoirJob.register.value, trigger='interval', seconds=10)
                case _:
                    logger.info(f'Invalid status change from {status} to {new_status}')

        case ReservoirStatus.initializing:
            logger.info('status: INITIALIZING')
            match new_status:
                case ReservoirStatus.registering:
                    logger.info('new_status: REGISTERING')
                    status = ReservoirStatus.registering
                    scheduler.add_job(func=lambda: system_connector.register_reservoir_with_system(id),
                                      id=ReservoirJob.register.value, trigger='interval', seconds=10)
                case _:
                    logger.info(f'Invalid status change from {status} to {new_status}')

        case ReservoirStatus.registering:
            logger.info('status: REGISTERING')
            match new_status:
                case ReservoirStatus.active:
                    logger.info('new_status: ACTIVE')
                    status = ReservoirStatus.active
                    scheduler.remove_job(job_id=ReservoirJob.register.value)
                    scheduler.add_job(func=lambda: system_connector.reservoir_health_check(id),
                                      id=ReservoirJob.health_check.value, trigger='interval', seconds=10)
                    scheduler.add_job(func=safety_check, id=ReservoirJob.safety_check.value, trigger='interval',
                                      seconds=10)
                case _:
                    logger.info(f'Invalid status change from {status} to {new_status}')

        case ReservoirStatus.started:
            logger.info('status: STARTED')
            match new_status:
                case ReservoirStatus.initializing:
                    logger.info('new_status: INITIALIZING')
                    status = ReservoirStatus.initializing
                case _:
                    logger.info(f'Invalid status change from {status} to {new_status}')

        case _:
            logger.info(f'status value not recognized: {status}')


def initialize(config_filename: str, _scheduler: BackgroundScheduler):
    global id, capacity, pid, port, scheduler, status, system_host
    logger.info('Initializing ReservoirService')
    change_status(ReservoirStatus.initializing)
    reservoir_config = file_util.load_json_file(config_filename)

    initialize_components(reservoir_config)

    id = reservoir_config['id']
    capacity = reservoir_config['capacity']
    pid = os.getpid()
    port = reservoir_config['port']
    scheduler = _scheduler
    system_host = reservoir_config['systemHost']

    change_status(ReservoirStatus.registering)


def initialize_components(reservoir_config):
    initialize_heaters(reservoir_config)
    initialize_level_sensor(reservoir_config)
    initialize_receiver_pumps(reservoir_config)
    initialize_receiver_valves(reservoir_config)
    initialize_send_pumps(reservoir_config)
    initialize_send_valves(reservoir_config)
    initialize_source_valves(reservoir_config)
    initialize_source_pumps(reservoir_config)
    initialize_thermometers(reservoir_config)
    initialize_water_jets(reservoir_config)


def initialize_heaters(reservoir_config):
    logger.info('In ReservoirService::initialize_heaters')
    for heater in reservoir_config['heaters']:
        logger.info(f'Initializing heater id: {heater["id"]}')
        heaters.append(Heater(heater['id'], heater['resourceKey'], heater['resourceType']))
    logger.info(f'{len(heaters)} heaters initialized')


def initialize_level_sensor(reservoir_config):
    global level_sensor
    logger.info('In ReservoirService::initialize_level_sensor')
    level_sensor = LevelSensor(reservoir_config['levelSensor']["id"])

    for _float_switch in reservoir_config['levelSensor']['floatSwitches']:
        logger.info(f'Initializing float switch id: {_float_switch["id"]}')
        level_sensor.add_float_switch(FloatSwitch(_float_switch['id'], _float_switch['level'], _float_switch['mode'], _float_switch['resourceKey'], _float_switch['resourceType']))
    logger.info(f'Level sensor initialized with {len(level_sensor.float_switches)} float switches')


def initialize_receiver_pumps(reservoir_config):
    logger.info('In ReservoirService::initialize_receiver_pumps')
    for receiver_pump in reservoir_config['receiverPumps']:
        logger.info(f'Initializing receiver pump id: {receiver_pump["id"]}')
        receiver_pumps.append(Pump(receiver_pump['id'], receiver_pump['resourceKey'], receiver_pump['resourceType']))
    logger.info(f'{len(receiver_pumps)} receiver pumps initialized')


def initialize_receiver_valves(reservoir_config):
    logger.info('In ReservoirService::initialize_receiver_valves')
    for receiver_valve in reservoir_config['receiverValves']:
        logger.info(f'Initializing receiver valve id: {receiver_valve["id"]}')
        receiver_valves.append(Valve(receiver_valve['id'], receiver_valve['resourceKey'], receiver_valve['resourceType']))
    logger.info(f'{len(receiver_valves)} receiver valves initialized')


def initialize_send_pumps(reservoir_config):
    logger.info('In ReservoirService::initialize_send_pumps')
    for send_pump in reservoir_config['sendPumps']:
        logger.info(f'Initializing send pump id: {send_pump["id"]}')
        send_pumps.append(Pump(send_pump['id'], send_pump['resourceKey'], send_pump['resourceType']))
    logger.info(f'{len(send_pumps)} send pumps initialized')


def initialize_send_valves(reservoir_config):
    logger.info('In ReservoirService::initialize_send_valves')
    for send_valve in reservoir_config['sendValves']:
        logger.info(f'Initializing send valve id: {send_valve["id"]}')
        send_valves.append(Valve(send_valve['id'], send_valve['resourceKey'], send_valve['resourceType']))
    logger.info(f'{len(send_valves)} send valves initialized')


def initialize_source_pumps(reservoir_config):
    logger.info('In ReservoirService::initialize_source_pumps')
    for source_pump in reservoir_config['sourcePumps']:
        logger.info(f'Initializing source pump id: {source_pump["id"]}')
        source_pumps.append(Pump(source_pump['id'], source_pump['resourceKey'], source_pump['resourceType']))
    logger.info(f'{len(source_pumps)} source pumps initialized')


def initialize_source_valves(reservoir_config):
    logger.info('In ReservoirService::initialize_source_valves')
    for source_valve in reservoir_config['sourceValves']:
        logger.info(f'Initializing source valve id: {source_valve["id"]}')
        source_valves.append(Valve(source_valve['id'], source_valve['resourceKey'], source_valve['resourceType']))
    logger.info(f'{len(source_valves)} source valves initialized')


def initialize_thermometers(reservoir_config):
    logger.info('In ReservoirService::initialize_thermometers')
    for thermometer in reservoir_config['thermometers']:
        logger.info(f'Initializing thermometer id: {thermometer["id"]}')
        thermometers.append(Thermometer(thermometer['id'], thermometer['resourceKey'], thermometer['resourceType']))
    logger.info(f'{len(thermometers)} thermometers initialized')


def initialize_water_jets(reservoir_config):
    logger.info('In ReservoirService::initialize_water_jets')
    for water_jet in reservoir_config['waterJets']:
        logger.info(f'Initializing water jet id: {water_jet["id"]}')
        water_jets.append(WaterJet(water_jet['id'], water_jet['resourceKey'], water_jet['resourceType']))
    logger.info(f'{len(water_jets)} water jets initialized')


def level_check() -> int:
    logger.info('Starting level check')
    return level_sensor_service.get_water_level(level_sensor)


def safety_check():
    logger.info('Starting safety check')
    _safe_levels: bool = level_sensor_service.safety_check(level_sensor)

    if not _safe_levels:
        logger.info('Water level safety check failed. Server exiting')
        os.kill(pid, 9)

    logger.info('Safety checks passed')
