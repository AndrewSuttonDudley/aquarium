from component.aquarium import Aquarium
from component.reservoir import Reservoir
from util import file_util


aquariums = dict()
reservoirs = dict()


def initialize(config_filename: str):
    print('Initializing SystemService')
    system_config = file_util.load_json_file(config_filename)
    initialize_aquariums(system_config)
    initialize_reservoirs(system_config)


def initialize_aquariums(system_config):
    print('In SystemService::initialize_aquariums')
    for aquarium in system_config['aquariums']:
        id = aquarium['id']
        print('Initializing aquarium id: ', id)
        aquariums[id] = Aquarium(id, aquarium['host'])
    print(f'{len(aquariums)} aquariums initialized')


def initialize_reservoirs(system_config):
    print('In SystemService::_initialize_reservoirs')
    for reservoir in system_config['reservoirs']:
        id = reservoir['id']
        print('Initializing reservoir id: ', id)
        reservoirs[id] = Reservoir(id, reservoir['host'])
    print(f'{len(reservoirs)} reservoirs initialized')


def register_aquarium(id: str):
    aquariums[id]['registered'] = True


def register_reservoir(id: str):
    reservoirs[id]['registered'] = True
