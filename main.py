from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import os

from flask import Flask
import logging
# from twilio.rest import Client

from controller.aquarium_controller import aquarium_bp
from controller.reservoir_controller import reservoir_bp
from controller.system_controller import system_bp
from service import aquarium_service, AquariumJob
from service import reservoir_service, ReservoirJob
from service import system_service, SystemJob


flask = Flask('aquarium')
handler = logging.FileHandler('aquarium.log')
# Todo: Fix this formatter
# handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
flask.logger.addHandler(handler)
flask.logger.setLevel(logging.INFO)
logger = flask.logger


@flask.route('/health', methods=['GET'])
def health():
    return 'healthy'


if __name__ == '__main__':
    server_role = os.environ.get('AQUARIUM_SERVER_ROLE')
    logger.info(f'server_role: {server_role}')
    logger.info(f'server_role[:8]: {server_role[:8]}')
    config_filename = f'config/{server_role}.config.json'
    logger.info(f'config_filename: {config_filename}')

    scheduler = BackgroundScheduler()
    port = -1
    if server_role[:8] == 'aquarium':
        aquarium_service.initialize(config_filename)
        aquarium_service.config[aquarium_service.SCHEDULER] = scheduler
        port = aquarium_service.config['port']
        flask.register_blueprint(aquarium_bp, url_prefix='/aquarium')
        aquarium_service.config[AquariumJob.REGISTER]\
            = scheduler.add_job(func=aquarium_service.register_with_system, id=ReservoirJob.REGISTER.value,
                                trigger='interval', seconds=6)

    elif server_role[:9] == 'reservoir':
        reservoir_service.initialize(config_filename)
        reservoir_service.config[reservoir_service.SCHEDULER] = scheduler
        port = reservoir_service.config['port']
        flask.register_blueprint(reservoir_bp, url_prefix='/reservoir')
        reservoir_service.config[ReservoirJob.REGISTER]\
            = scheduler.add_job(func=reservoir_service.register_with_system, id=ReservoirJob.REGISTER.value,
                                trigger='interval', seconds=6)

    elif server_role == 'system':
        system_service.initialize(config_filename)
        system_service.config[system_service.SCHEDULER] = scheduler
        port = system_service.config['port']
        flask.register_blueprint(system_bp, url_prefix='/system')
        scheduler.add_job(func=system_service.wait_for_servers_to_register, id=SystemJob.REGISTRATION.value, trigger='interval', seconds=5)

    else:
        raise 'Required environment variable AQUARIUM_SERVER_ROLE not found. Server not starting.'

    logger.info('Starting initial scheduled tasks')
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

    logger.info('Running flask app')
    flask.run(port=port)  # (debug=True)
