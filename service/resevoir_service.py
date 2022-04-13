from component.heater import Heater
from component.level_sensor import LevelSensor
from component.pump import Pump
from component.thermometer import Thermometer
from component.valve import Valve
from component.water_jet import WaterJet
from util import file_util


config = dict()
heaters = []
level_sensors = []
receiver_pumps = []
receiver_valves = []
send_pumps = []
send_valves = []
source_pumps = []
source_valves = []
thermometers = []
water_jets = []


def initialize(config_filename: str):
    print('Initializing ReservoirService')
    reservoir_config = file_util.load_json_file(config_filename)
    initialize_components(reservoir_config)


def initialize_components(reservoir_config):
    config['system_host'] = reservoir_config['systemHost']
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
    print('In ReservoirService::initialize_heaters')
    for heater in reservoir_config['heaters']:
        print('Initializing heater id: ', heater['id'])
        heaters.append(Heater(heater['id'], heater['resourceKey']))
    print(f'{len(heaters)} heaters initialized')


def initialize_level_sensors(reservoir_config):
    print('In ReservoirService::initialize_level_sensors')
    for level_sensor in reservoir_config['levelSensors']:
        print('Initializing level sensor id: ', level_sensor['id'])
        level_sensors.append(LevelSensor(level_sensor['id'], level_sensor['resourceKey']))
    print(f'{len(level_sensors)} level sensors initialized')


def initialize_receiver_pumps(reservoir_config):
    print('In ReservoirService::initialize_receiver_pumps')
    for receiver_pump in reservoir_config['receiverPumps']:
        print('Initializing receiver pump id: ', receiver_pump['id'])
        receiver_pumps.append(Pump(receiver_pump['id'], receiver_pump['resourceKey']))
    print(f'{len(receiver_pumps)} receiver pumps initialized')


def initialize_receiver_valves(reservoir_config):
    print('In ReservoirService::initialize_receiver_valves')
    for receiver_valve in reservoir_config['receiverValves']:
        print('Initializing receiver valve id: ', receiver_valve['id'])
        receiver_valves.append(Valve(receiver_valve['id'], receiver_valve['resourceKey']))
    print(f'{len(receiver_valves)} receiver valves initialized')


def initialize_send_pumps(reservoir_config):
    print('In ReservoirService::initialize_send_pumps')
    for send_pump in reservoir_config['sendPumps']:
        print('Initializing send pump id: ', send_pump['id'])
        send_pumps.append(Pump(send_pump['id'], send_pump['resourceKey']))
    print(f'{len(send_pumps)} send pumps initialized')


def initialize_send_valves(reservoir_config):
    print('In ReservoirService::initialize_send_valves')
    for send_valve in reservoir_config['sendValves']:
        print('Initializing send valve id: ', send_valve['id'])
        send_valves.append(Valve(send_valve['id'], send_valve['resourceKey']))
    print(f'{len(send_valves)} send valves initialized')


def initialize_source_pumps(reservoir_config):
    print('In ReservoirService::initialize_source_pumps')
    for source_pump in reservoir_config['sourcePumps']:
        print('Initializing source pump id: ', source_pump['id'])
        source_pumps.append(Pump(source_pump['id'], source_pump['resourceKey']))
    print(f'{len(source_pumps)} source pumps initialized')


def initialize_source_valves(reservoir_config):
    print('In ReservoirService::initialize_source_valves')
    for source_valve in reservoir_config['sourceValves']:
        print('Initializing source valve id: ', source_valve['id'])
        source_valves.append(Valve(source_valve['id'], source_valve['resourceKey']))
    print(f'{len(source_valves)} source valves initialized')


def initialize_thermometers(reservoir_config):
    print('In ReservoirService::initialize_thermometers')
    for thermometer in reservoir_config['thermometers']:
        print('Initializing thermometer id: ', thermometer['id'])
        thermometers.append(Thermometer(thermometer['id'], thermometer['resourceKey']))
    print(f'{len(thermometers)} thermometers initialized')


def initialize_water_jets(reservoir_config):
    print('In ReservoirService::initialize_water_jets')
    for water_jet in reservoir_config['waterJets']:
        print('Initializing water jet id: ', water_jet['id'])
        water_jets.append(WaterJet(water_jet['id'], water_jet['resourceKey']))
    print(f'{len(water_jets)} water jets initialized')
