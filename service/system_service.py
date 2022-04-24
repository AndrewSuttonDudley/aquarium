from flask import abort
from apscheduler.schedulers.background import BackgroundScheduler
from enum import Enum
import logging
from typing import Optional
import os

from component.aquarium import Aquarium
from connector import aquarium_connector
from util import file_util
from component.reservoir import Reservoir
from connector import reservoir_connector
from component.schedule import Schedule


logger = logging.getLogger('aquarium.system_service')


class SystemJob(Enum):
    health_check = 'health_check'
    level_check = 'level_check'
    temperature_check = 'temperature_check'
    water_change = 'water_change'


class SystemStatus(Enum):
    started = 'started'
    initializing = 'initializing'
    active = 'active'


id: Optional[str] = None
aquariums: dict[str, Aquarium] = dict()
pid: Optional[int] = None
port: Optional[int] = None
reservoirs: dict[str, Reservoir] = dict()
scheduler: Optional[BackgroundScheduler] = None
status = SystemStatus.started.value
timezone: Optional[str] = None


def aquarium_health_check(aquarium_id: str):
    if not aquariums[aquarium_id].registered:
        logger.info(f'Aquarium not registered. Returning 409 Conflict from health_check for aquarium id: {aquarium_id}')
        abort(409)


def reservoir_health_check(reservoir_id: str):
    if not reservoirs[reservoir_id].registered:
        logger.info(f'Reservoir not registered. Returning 409 Conflict from health_check for reservoir id: {reservoir_id}')
        abort(409)


def health_checks():
    _server_count = registered_server_count()
    if _server_count == 0:
        return
    logger.info(f'Running {_server_count} health checks')
    for _aquarium in aquariums.values():
        if _aquarium.registered:
            if not aquarium_connector.health_check(_aquarium.id):
                unregister_aquarium(_aquarium.id)

    for _reservoir in reservoirs.values():
        if _reservoir.registered:
            if not reservoir_connector.health_check(_reservoir.id):
                unregister_reservoir(_reservoir.id)


def initialize(config_filename: str, _scheduler: BackgroundScheduler) -> bool:
    global id, pid, port, scheduler, shutdown, status, timezone
    status = SystemStatus.initializing
    logger.info('Initializing SystemService')
    system_config = file_util.load_json_file(config_filename)

    result: bool = validate_schedules(system_config)
    initialize_aquariums(system_config)
    initialize_reservoirs(system_config)

    id = system_config['id']
    pid = os.getpid()
    port = system_config['port']
    scheduler = _scheduler
    status = SystemStatus.active
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


def start_aquarium_level_check(aquarium_id: str):
    logger.info(f'Starting level check for aquarium (id: {aquarium_id})')
    _aquarium = aquariums[aquarium_id]
    _level = aquarium_connector.level_check(_aquarium.id)
    logger.info(f'Aquarium (id: {_aquarium.id}) level is {_level}%')


def start_aquarium_schedules(_aquarium: Aquarium):
    logger.info(f'Starting schedules for aquarium: {_aquarium.to_string()}')
    for schedule in _aquarium.schedules:
        logger.info(f'Starting schedule: {schedule.to_string()}')
        match schedule.type:
            case SystemJob.level_check.value:
                scheduler.add_job(func=lambda: start_aquarium_level_check(_aquarium.id), id=schedule.id,
                                  trigger='cron', hour=schedule.hour, minute=schedule.minute, timezone=timezone)
            case SystemJob.temperature_check.value:
                scheduler.add_job(func=lambda: start_aquarium_temperature_check(_aquarium.id), id=schedule.id,
                                  trigger='cron', hour=schedule.hour, minute=schedule.minute, timezone=timezone)
            case SystemJob.water_change.value:
                scheduler.add_job(func=lambda: start_aquarium_water_change(_aquarium.id), id=schedule.id,
                                  trigger='cron', hour=schedule.hour, minute=schedule.minute, timezone=timezone)
            case _:
                logger.error(f'Schedule type "{schedule.type}" not found')


def start_aquarium_temperature_check(aquarium_id: str):
    logger.info(f'Starting temperature check for aquarium (id: {aquarium_id})')


def start_aquarium_water_change(aquarium_id: str):
    logger.info(f'Starting water change for aquarium (id: {aquarium_id})')


def start_health_check_job():
    logger.info('Starting health checks')
    scheduler.add_job(func=health_checks, id=SystemJob.health_check.value, trigger='interval', seconds=10)


def start_reservoir_level_check(_reservoir_id: str):
    logger.info(f'Starting level check for reservoir (id: {_reservoir_id})')
    _reservoir = reservoirs[_reservoir_id]
    _level = reservoir_connector.level_check(_reservoir.id)
    logger.info(f'Reservoir (id: {_reservoir.id}) level is {_level}%')


def start_reservoir_schedules(_reservoir: Reservoir):
    logger.info(f'Starting schedules for reservoir: {_reservoir.to_string()}')
    for _schedule in _reservoir.schedules:
        logger.info(f'Starting schedule: {_schedule.to_string()}')
        match _schedule.type:
            case SystemJob.level_check.value:
                scheduler.add_job(func=lambda: start_reservoir_level_check(_reservoir.id),
                                  id=f'{SystemJob.level_check.value}_{_reservoir.id}', trigger='cron',
                                  hour=_schedule.hour, minute=_schedule.minute, timezone=timezone)
            case SystemJob.temperature_check.value:
                scheduler.add_job(func=lambda: start_reservoir_temperature_check(_reservoir.id),
                                  id=f'{SystemJob.temperature_check.value}_{_reservoir.id}', trigger='cron',
                                  hour=_schedule.hour, minute=_schedule.minute, timezone=timezone)
            case _:
                logger.error(f'Schedule type "{_schedule.type}" not found')


def start_reservoir_temperature_check(_reservoir_id: str):
    logger.info(f'Starting temperature check for reservoir (id: {_reservoir_id})')


def unregister_aquarium(_aquarium_id: str):
    logger.info(f'Unregistering aquarium id: {_aquarium_id}')
    aquariums[_aquarium_id].registered = False
    for _schedule in aquariums[_aquarium_id].schedules:
        scheduler.remove_job(job_id=_schedule.id)


def unregister_reservoir(_reservoir_id: str):
    logger.info(f'Unregistering reservoir id: {_reservoir_id}')
    reservoirs[_reservoir_id].registered = False
    for _schedule in reservoirs[_reservoir_id].schedules:
        scheduler.remove_job(job_id=_schedule.id)
