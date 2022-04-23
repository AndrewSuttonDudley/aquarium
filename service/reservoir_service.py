import apscheduler.job
from apscheduler.schedulers.background import BackgroundScheduler
from enum import Enum
from util import file_util
import logging
from typing import Optional

from component.heater import Heater
from component.level_sensor import LevelSensor
from component.pump import Pump
from connector import reservoir_connector
from component.thermometer import Thermometer
from component.valve import Valve
from component.water_jet import WaterJet


logger = logging.getLogger('aquarium.reservoir_service')


class ReservoirJob(Enum):
    REGISTER = 'register'
    HEALTH_CHECK = 'health_check'


class ReservoirStatus(Enum):
    STARTED = 'started'
    INITIALIZING = 'initializing'
    REGISTERING = 'registering'
    ACTIVE = 'active'


SCHEDULER = 'scheduler'

id: Optional[str] = None
capacity: Optional[int] = None
heaters = []
level_sensors = []
port: Optional[int] = None
receiver_pumps = []
receiver_valves = []
scheduler: Optional[BackgroundScheduler] = None
send_pumps = []
send_valves = []
source_pumps = []
source_valves = []
status = ReservoirStatus.STARTED
system_host: Optional[str] = None
thermometers = []
water_jets = []


def change_status(new_status: ReservoirStatus):
    global status
    logger.info(f'Changing reservoir status from {status} to {new_status}')
    match status:
        case ReservoirStatus.ACTIVE:
            logger.info('status: ACTIVE')
            match new_status:
                case ReservoirStatus.REGISTERING:
                    logger.info('new_status: REGISTERING')
                    status = ReservoirStatus.REGISTERING
                    logger.info(f'Removing health check job with ID: {ReservoirJob.HEALTH_CHECK.value}. Existing jobs:')
                    for job in scheduler.get_jobs():
                        logger.info(f'Job ID: {job.id}')
                    scheduler.remove_job(job_id=ReservoirJob.HEALTH_CHECK.value)
                    for job in scheduler.get_jobs():
                        logger.info(f'Job ID: {job.id}')
                    scheduler.add_job(func=reservoir_connector.register_with_system, id=ReservoirJob.REGISTER.value,
                                      trigger='interval', seconds=10)
                case _:
                    logger.info(f'Invalid status change from {status} to {new_status}')

        case ReservoirStatus.INITIALIZING:
            logger.info('status: INITIALIZING')
            match new_status:
                case ReservoirStatus.REGISTERING:
                    logger.info('new_status: REGISTERING')
                    status = ReservoirStatus.REGISTERING
                    scheduler.add_job(func=reservoir_connector.register_with_system, id=ReservoirJob.REGISTER.value,
                                      trigger='interval', seconds=10)
                case _:
                    logger.info(f'Invalid status change from {status} to {new_status}')

        case ReservoirStatus.REGISTERING:
            logger.info('status: REGISTERING')
            match new_status:
                case ReservoirStatus.ACTIVE:
                    logger.info('new_status: ACTIVE')
                    status = ReservoirStatus.ACTIVE
                    scheduler.remove_job(job_id=ReservoirJob.REGISTER.value)
                    scheduler.add_job(func=lambda: reservoir_connector.system_health_check(id), id=ReservoirJob.HEALTH_CHECK.value,
                                      trigger='interval', seconds=10)
                case _:
                    logger.info(f'Invalid status change from {status} to {new_status}')

        case ReservoirStatus.STARTED:
            logger.info('status: STARTED')
            match new_status:
                case ReservoirStatus.INITIALIZING:
                    logger.info('new_status: INITIALIZING')
                    status = ReservoirStatus.INITIALIZING
                case _:
                    logger.info(f'Invalid status change from {status} to {new_status}')

        case _:
            logger.info(f'status value not recognized: {status}')


def initialize(config_filename: str, _scheduler: BackgroundScheduler):
    global id, capacity, port, scheduler, status, system_host
    logger.info('Initializing ReservoirService')
    change_status(ReservoirStatus.INITIALIZING)
    reservoir_config = file_util.load_json_file(config_filename)

    initialize_components(reservoir_config)

    id = reservoir_config['id']
    capacity = reservoir_config['capacity']
    port = reservoir_config['port']
    scheduler = _scheduler
    system_host = reservoir_config['systemHost']

    change_status(ReservoirStatus.REGISTERING)


def initialize_components(reservoir_config):
    initialize_heaters(reservoir_config)
    initialize_level_sensors(reservoir_config)
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
        heaters.append(Heater(heater['id'], heater['resourceKey']))
    logger.info(f'{len(heaters)} heaters initialized')


def initialize_level_sensors(reservoir_config):
    logger.info('In ReservoirService::initialize_level_sensors')
    for level_sensor in reservoir_config['levelSensors']:
        logger.info(f'Initializing level sensor id: {level_sensor["id"]}')
        level_sensors.append(LevelSensor(level_sensor['id'], level_sensor['resourceKey']))
    logger.info(f'{len(level_sensors)} level sensors initialized')


def initialize_receiver_pumps(reservoir_config):
    logger.info('In ReservoirService::initialize_receiver_pumps')
    for receiver_pump in reservoir_config['receiverPumps']:
        logger.info(f'Initializing receiver pump id: {receiver_pump["id"]}')
        receiver_pumps.append(Pump(receiver_pump['id'], receiver_pump['resourceKey']))
    logger.info(f'{len(receiver_pumps)} receiver pumps initialized')


def initialize_receiver_valves(reservoir_config):
    logger.info('In ReservoirService::initialize_receiver_valves')
    for receiver_valve in reservoir_config['receiverValves']:
        logger.info(f'Initializing receiver valve id: {receiver_valve["id"]}')
        receiver_valves.append(Valve(receiver_valve['id'], receiver_valve['resourceKey']))
    logger.info(f'{len(receiver_valves)} receiver valves initialized')


def initialize_send_pumps(reservoir_config):
    logger.info('In ReservoirService::initialize_send_pumps')
    for send_pump in reservoir_config['sendPumps']:
        logger.info(f'Initializing send pump id: {send_pump["id"]}')
        send_pumps.append(Pump(send_pump['id'], send_pump['resourceKey']))
    logger.info(f'{len(send_pumps)} send pumps initialized')


def initialize_send_valves(reservoir_config):
    logger.info('In ReservoirService::initialize_send_valves')
    for send_valve in reservoir_config['sendValves']:
        logger.info(f'Initializing send valve id: {send_valve["id"]}')
        send_valves.append(Valve(send_valve['id'], send_valve['resourceKey']))
    logger.info(f'{len(send_valves)} send valves initialized')


def initialize_source_pumps(reservoir_config):
    logger.info('In ReservoirService::initialize_source_pumps')
    for source_pump in reservoir_config['sourcePumps']:
        logger.info(f'Initializing source pump id: {source_pump["id"]}')
        source_pumps.append(Pump(source_pump['id'], source_pump['resourceKey']))
    logger.info(f'{len(source_pumps)} source pumps initialized')


def initialize_source_valves(reservoir_config):
    logger.info('In ReservoirService::initialize_source_valves')
    for source_valve in reservoir_config['sourceValves']:
        logger.info(f'Initializing source valve id: {source_valve["id"]}')
        source_valves.append(Valve(source_valve['id'], source_valve['resourceKey']))
    logger.info(f'{len(source_valves)} source valves initialized')


def initialize_thermometers(reservoir_config):
    logger.info('In ReservoirService::initialize_thermometers')
    for thermometer in reservoir_config['thermometers']:
        logger.info(f'Initializing thermometer id: {thermometer["id"]}')
        thermometers.append(Thermometer(thermometer['id'], thermometer['resourceKey']))
    logger.info(f'{len(thermometers)} thermometers initialized')


def initialize_water_jets(reservoir_config):
    logger.info('In ReservoirService::initialize_water_jets')
    for water_jet in reservoir_config['waterJets']:
        logger.info(f'Initializing water jet id: {water_jet["id"]}')
        water_jets.append(WaterJet(water_jet['id'], water_jet['resourceKey']))
    logger.info(f'{len(water_jets)} water jets initialized')
