from flask import abort
from apscheduler.schedulers.background import BackgroundScheduler
from enum import Enum
import logging
import math
import requests
from typing import Optional

from component.aquarium import Aquarium
from component.reservoir import Reservoir
from component.schedule import Schedule
from util import file_util


logger = logging.getLogger('aquarium.system_service')


class SystemJob(Enum):
    HEALTH_CHECK = 'health_check'
    LEVEL_CHECK = 'level_check'
    TEMPERATURE_CHECK = 'temperature_check'
    WATER_CHANGE = 'water_change'


class SystemStatus(Enum):
    STARTED = 'started'
    INITIALIZING = 'initializing'
    ACTIVE = 'active'


id: Optional[str] = None
aquariums: dict[str, Aquarium] = dict()
port: Optional[int] = None
reservoirs: dict[str, Reservoir] = dict()
scheduler: Optional[BackgroundScheduler] = None
status = SystemStatus.STARTED.value
timezone: Optional[str] = None


def aquarium_health_check(aquarium_id: str):
    logger.info(f'aquariums[aquarium_id].registered: {aquariums[aquarium_id].registered}')
    if not aquariums[aquarium_id].registered:
        logger.info(f'Aquarium not registered. Returning 409 Conflict from health_check for aquarium id: {aquarium_id}')
        abort(409)


def reservoir_health_check(reservoir_id: str):
    logger.info(f'reservoirs[reservoir_id].registered: {reservoirs[reservoir_id].registered}')
    if not reservoirs[reservoir_id].registered:
        logger.info(f'Reservoir not registered. Returning 409 Conflict from health_check for reservoir id: {reservoir_id}')
        abort(409)


def health_checks():
    server_count = registered_server_count()
    if server_count == 0:
        return
    logger.info(f'Running {server_count} health checks')
    for aquarium in aquariums.values():
        if aquarium.registered:
            url = f'{aquarium.host}/health-check'
            logger.info(f'Checking health of {aquarium.name} at url: {url}')
            try:
                response = requests.get(url)
            except OSError:
                logger.info(f'Aquarium not found. Unregistering {aquarium.name}')
                aquarium.registered = False
            else:
                if math.floor(response.status_code / 100) == 2:
                    logger.info(f'{aquarium.name} is healthy')
                else:
                    logger.info(f'{aquarium.name} health check returned {response.status_code} status code. Unregistering aquarium')
                    aquarium.registered = False

    for reservoir in reservoirs.values():
        if reservoir.registered:
            url = f'{reservoir.host}/health-check'
            logger.info(f'Checking health of {reservoir.name} at url: {url}')
            try:
                response = requests.get(url)
            except OSError:
                logger.info(f'Reservoir not found. Unregistering {reservoir.name}')
                reservoir.registered = False
            else:
                if math.floor(response.status_code / 100) == 2:
                    logger.info(f'{reservoir.name} is healthy')
                else:
                    logger.info(f'{reservoir.name} health check returned {response.status_code} status code. Unregistering reservoir')
                    reservoir.registered = False


def initialize(config_filename: str, _scheduler: BackgroundScheduler) -> bool:
    global id, port, scheduler, status, timezone
    status = SystemStatus.INITIALIZING
    logger.info('Initializing SystemService')
    system_config = file_util.load_json_file(config_filename)

    result: bool = validate_schedules(system_config)
    initialize_aquariums(system_config)
    initialize_reservoirs(system_config)

    id = system_config['id']
    port = system_config['port']
    scheduler = _scheduler
    status = SystemStatus.ACTIVE
    timezone = system_config['timezone']

    start_health_check_job()
    return result


def initialize_aquariums(system_config: dict):
    logger.info('Initializing Aquariums')
    for aquarium in system_config['aquariums']:
        _id = aquarium['id']
        aquariums[_id] = Aquarium(_id, aquarium['capacity'], aquarium['host'], aquarium['name'])
        logger.info(f'Initializing aquarium: {_id}')
        aquariums[_id].schedules.extend(initialize_schedules(aquarium['schedules']))
        logger.info(f'{len(aquariums[_id].schedules)} schedules initialized')
    logger.info(f'{len(aquariums)} aquariums initialized')


def initialize_reservoirs(system_config: dict):
    logger.info('Initializing Reservoirs')
    for reservoir in system_config['reservoirs']:
        r = Reservoir(reservoir['id'], reservoir['capacity'], reservoir['host'], reservoir['name'])
        logger.info(f'Initializing reservoir: {r.to_string()}')
        reservoirs[r.id] = r
        r.schedules.extend(initialize_schedules(reservoir['schedules']))
        logger.info(f'{len(r.schedules)} schedules initialized')
    logger.info(f'{len(reservoirs)} reservoirs initialized')


def validate_schedules(system_config: dict) -> bool:
    logger.info('Validating schedules')
    ids: [str] = []
    for aquarium in system_config['aquariums']:
        for schedule in aquarium['schedules']:
            logger.info(f'Checking schedule id: {schedule["id"]}')
            if schedule['id'] in ids:
                return False
            ids.append(schedule['id'])
    for reservoir in system_config['reservoirs']:
        for schedule in reservoir['schedules']:
            logger.info(f'Checking schedule id: {schedule["id"]}')
            if schedule['id'] in ids:
                return False
            ids.append(schedule['id'])
    return True


def initialize_schedules(_schedules: 'list[dict]') -> 'list[Schedule]':
    logger.info('Initializing schedules')
    s = []
    for _schedule in _schedules:
        schedule = Schedule(_schedule['id'], _schedule['day_of_week'], _schedule['hour'], _schedule['minute'],
                                   _schedule['percent_change'], _schedule['type'])
        logger.info(f'Initializing schedule: {schedule.to_string()}')
        s.append(schedule)
    return s


def register_aquarium(_id: str) -> Aquarium:
    aquariums[_id].registered = True
    logger.info(f'Aquarium id: {_id} registered!')
    start_aquarium_schedules(aquariums[_id])
    return aquariums[_id]


def register_reservoir(_id: str) -> Reservoir:
    reservoirs[_id].registered = True
    logger.info(f'Reservoir id: {_id} registered!')
    start_reservoir_schedules(reservoirs[_id])
    return reservoirs[_id]


def registered_server_count() -> int:
    server_count = 0
    for aquarium in aquariums.values():
        if aquarium.registered:
            server_count = server_count + 1
    for reservoir in reservoirs.values():
        if reservoir.registered:
            server_count = server_count + 1
    return server_count


def start_aquarium_level_check(aquarium_id: int):
    logger.info(f'Starting level check for aquarium (id: {aquarium_id})')


def start_aquarium_schedules(aquarium: Aquarium):
    logger.info(f'Starting schedules for aquarium: {aquarium.to_string()}')
    for schedule in aquarium.schedules:
        logger.info(f'Starting schedule: {schedule.to_string()}')
        match schedule.type:
            case SystemJob.LEVEL_CHECK.value:
                scheduler.add_job(func=lambda: start_aquarium_level_check(aquarium.id), id=schedule.id,
                                  trigger='cron', hour=schedule.hour, minute=schedule.minute, timezone=timezone)
            case SystemJob.TEMPERATURE_CHECK.value:
                scheduler.add_job(func=lambda: start_aquarium_temperature_check(aquarium.id), id=schedule.id,
                                  trigger='cron', hour=schedule.hour, minute=schedule.minute, timezone=timezone)
            case SystemJob.WATER_CHANGE.value:
                scheduler.add_job(func=lambda: start_aquarium_water_change(aquarium.id), id=schedule.id,
                                  trigger='cron', hour=schedule.hour, minute=schedule.minute, timezone=timezone)
            case _:
                logger.error(f'Schedule type "{schedule.type}" not found')


def start_aquarium_temperature_check(aquarium_id: int):
    logger.info(f'Starting temperature check for aquarium (id: {aquarium_id})')


def start_aquarium_water_change(aquarium_id: int):
    logger.info(f'Starting water change for aquarium (id: {aquarium_id})')


def start_health_check_job():
    logger.info('Starting health checks')
    scheduler.add_job(func=health_checks, id=SystemJob.HEALTH_CHECK.value, trigger='interval', seconds=10)


def start_reservoir_schedules(reservoir: Reservoir):
    logger.info(f'Starting schedules for reservoir: {reservoir.to_string()}')
    for schedule in reservoir.schedules:
        logger.info(f'Starting schedule: {schedule.to_string()}')
        match schedule.type:
            case SystemJob.LEVEL_CHECK.value:
                scheduler.add_job(func=lambda: start_reservoir_level_check(reservoir.id),
                                  id=f'{SystemJob.LEVEL_CHECK.value}_{reservoir.id}',
                                  trigger='cron', hour=schedule.hour, minute=schedule.minute, timezone=timezone)
            case SystemJob.TEMPERATURE_CHECK.value:
                scheduler.add_job(func=lambda: start_reservoir_temperature_check(reservoir.id),
                                  id=f'{SystemJob.TEMPERATURE_CHECK.value}_{reservoir.id}',
                                  trigger='cron', hour=schedule.hour, minute=schedule.minute, timezone=timezone)
            case _:
                logger.error(f'Schedule type "{schedule.type}" not found')


def start_reservoir_level_check(reservoir_id: int):
    logger.info(f'Starting level check for reservoir (id: {reservoir_id})')


def start_reservoir_temperature_check(reservoir_id: int):
    logger.info(f'Starting temperature check for reservoir (id: {reservoir_id})')
