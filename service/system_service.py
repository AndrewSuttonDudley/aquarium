import logging

from component.aquarium import Aquarium
from component.reservoir import Reservoir
from util import file_util


logger = logging.getLogger('aquarium.system_service')

aquariums = dict()
config = dict()
reservoirs = dict()


def initialize(config_filename: str):
    logger.info('Initializing SystemService')
    system_config = file_util.load_json_file(config_filename)
    config['port'] = system_config['port']
    initialize_aquariums(system_config)
    initialize_reservoirs(system_config)


def initialize_aquariums(system_config):
    logger.info('Initializing SystemService')
    for aquarium in system_config['aquariums']:
        id = aquarium['id']
        logger.info(f'Initializing aquarium id: {id}')
        aquariums[id] = Aquarium(id, aquarium['host'])
    logger.info(f'{len(aquariums)} aquariums initialized')


def initialize_reservoirs(system_config):
    logger.info('Initializing SystemService')
    for reservoir in system_config['reservoirs']:
        id = reservoir['id']
        logger.info(f'Initializing reservoir id: {id}')
        reservoirs[id] = Reservoir(id, reservoir['host'])
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
    not_registered = []
    for aquarium_id in aquariums.keys():
        if not aquariums[aquarium_id].registered:
            not_registered.append(aquarium_id)
    for reservoir_id in reservoirs.keys():
        if not reservoirs[reservoir_id].registered:
            not_registered.append(reservoir_id)
    logger.info(f'Waiting for servers to register: {", ".join(not_registered)}')
