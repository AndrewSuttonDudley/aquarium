from enum import Enum
import logging

from component.aquarium import Aquarium
from component.reservoir import Reservoir
from component.schedule import Schedule
from util import file_util


logger = logging.getLogger('aquarium.system_service')


class SystemJob(Enum):
    REGISTRATION = 'registration'


class SystemStatus(Enum):
    STARTED = 'started'
    INITIALIZED = 'initialized'
    ACTIVE = 'active'


SCHEDULER = 'scheduler'

aquariums = dict()
config = dict()
reservoirs = dict()
schedules = []
status = SystemStatus.STARTED.value


def initialize(config_filename: str):
    global status
    logger.info('Initializing SystemService')
    system_config = file_util.load_json_file(config_filename)
    config['port'] = system_config['port']
    initialize_aquariums(system_config)
    initialize_reservoirs(system_config)
    status = SystemStatus.INITIALIZED.value


def initialize_aquariums(system_config):
    logger.info('Initializing Aquariums')
    for aquarium in system_config['aquariums']:
        a = Aquarium(aquarium['id'], aquarium['capacity'], aquarium['host'], aquarium['name'])
        logger.info(f'Initializing aquarium: {a.to_string()}')
        aquariums[a.id] = a

        for schedule in aquarium['schedules']:
            s = Schedule(schedule['id'], schedule['type'], schedule['cron'])
            logger.info(f'Initializing aquarium schedule: {s.to_string()}')
            a.schedules.append(s)

    logger.info(f'{len(aquariums)} aquariums initialized')


def initialize_reservoirs(system_config):
    logger.info('Initializing Reservoirs')
    for reservoir in system_config['reservoirs']:
        r = Reservoir(reservoir['id'], reservoir['capacity'], reservoir['host'], reservoir['name'])
        logger.info(f'Initializing reservoir: {r.to_string()}')
        reservoirs[r.id] = r

        for schedule in reservoir['schedules']:
            s = Schedule(schedule['id'], schedule['type'], schedule['cron'])
            logger.info(f'Initializing reservoir schedule: {s.to_string()}')
            r.schedules.append(s)

    logger.info(f'{len(reservoirs)} reservoirs initialized')


def register_aquarium(id: str) -> Aquarium:
    logger.info(f'Aquarium id: {id} registered!')
    aquariums[id].registered = True
    return aquariums[id]


def register_reservoir(id: str) -> Reservoir:
    logger.info(f'Reservoir id: {id} registered!')
    reservoirs[id].registered = True
    return reservoirs[id]


def wait_for_servers_to_register():
    global status
    logger.info(f'System status: {status}')
    not_registered = []
    for aquarium_id in aquariums.keys():
        if not aquariums[aquarium_id].registered:
            not_registered.append(aquarium_id)
    for reservoir_id in reservoirs.keys():
        if not reservoirs[reservoir_id].registered:
            not_registered.append(reservoir_id)

    if len(not_registered) == 0:
        logger.info('All servers have registered!')
        config[SCHEDULER].remove_job(job_id=SystemJob.REGISTRATION.value)
        status = SystemStatus.ACTIVE
    else:
        logger.info(f'Waiting for servers to register: {", ".join(not_registered)}')
