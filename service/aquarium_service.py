from component.heater import Heater
from component.level_sensor import LevelSensor
from component.pump import Pump
from component.thermometer import Thermometer
from component.water_jet import WaterJet
from util import file_util


aquarium = dict()
config = dict()
filter_pumps = []
heaters = []
level_sensors = []
thermometers = []
water_jets = []


def initialize(config_filename: str):
    print('Initializing AquariumService')
    aquarium_config = file_util.load_json_file(config_filename)
    initialize_components(aquarium_config)


def initialize_components(aquarium_config):
    initialize_filter_pumps(aquarium_config)
    initialize_heaters(aquarium_config)
    initialize_level_sensors(aquarium_config)
    config['system_host'] = aquarium_config['systemHost']
    initialize_thermometers(aquarium_config)
    initialize_water_jets(aquarium_config)


def initialize_filter_pumps(aquarium_config):
    print('In AquariumService::initialize_filter_pumps')
    for filter_pump in aquarium_config['filterPumps']:
        print('Initializing source pump id: ', filter_pump['id'])
        filter_pumps.append(Pump(filter_pump['id'], filter_pump['resourceKey']))
    print(f'{len(filter_pumps)} filter pumps initialized')


def initialize_heaters(aquarium_config):
    print('In AquariumService::initialize_heaters')
    for heater in aquarium_config['heaters']:
        print('Initializing heater id: ', heater['id'])
        heaters.append(Heater(heater['id'], heater['resourceKey']))
    print(f'{len(heaters)} heaters initialized')


def initialize_level_sensors(aquarium_config):
    print('In AquariumService::initialize_level_sensors')
    for level_sensor in aquarium_config['levelSensors']:
        print('Initializing level sensor id: ', level_sensor['id'])
        level_sensors.append(LevelSensor(level_sensor['id'], level_sensor['resourceKey']))
    print(f'{len(level_sensors)} level sensors initialized')


def initialize_thermometers(aquarium_config):
    print('In AquariumService::initialize_thermometers')
    for thermometer in aquarium_config['thermometers']:
        print('Initializing thermometer id: ', thermometer['id'])
        thermometers.append(Thermometer(thermometer['id'], thermometer['resourceKey']))
    print(f'{len(thermometers)} thermometers initialized')


def initialize_water_jets(aquarium_config):
    print('In AquariumService::initialize_water_jets')
    for water_jet in aquarium_config['waterJets']:
        print('Initializing water jet id: ', water_jet['id'])
        water_jets.append(WaterJet(water_jet['id'], water_jet['resourceKey']))
    print(f'{len(water_jets)} water jets initialized')
