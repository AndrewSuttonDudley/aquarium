from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import os
import typing

from flask import Flask
import logging
# from twilio.rest import Client

from controller.aquarium_controller import aquarium_bp
from controller.reservoir_controller import reservoir_bp
from controller.system_controller import system_bp
from service import aquarium_service
from service import reservoir_service
from service import system_service


flask = Flask('aquarium')
handler = logging.FileHandler('aquarium.log')
# Todo: Fix this formatter
# handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
flask.logger.addHandler(handler)
flask.logger.setLevel(logging.INFO)
logger = flask.logger


if __name__ == '__main__':
    server_role = os.environ.get('AQUARIUM_SERVER_ROLE')
    logger.info(f'server_role: {server_role}')
    config_filename = f'config/{server_role}.config.json'
    logger.info(f'config_filename: {config_filename}')

    scheduler = BackgroundScheduler()
    port: typing.Optional[int] = None
    init_result = True
    if server_role[:8] == 'aquarium':
        aquarium_service.initialize(config_filename, scheduler)
        port = aquarium_service.port
        flask.register_blueprint(aquarium_bp, url_prefix='/aquarium')
    elif server_role[:9] == 'reservoir':
        reservoir_service.initialize(config_filename, scheduler)
        port = reservoir_service.port
        flask.register_blueprint(reservoir_bp, url_prefix='/reservoir')
    elif server_role == 'system':
        init_result = system_service.initialize(config_filename, scheduler)
        port = system_service.port
        flask.register_blueprint(system_bp, url_prefix='/system')
    else:
        raise 'Required environment variable AQUARIUM_SERVER_ROLE not found. Server not starting.'

    if port is None:
        logger.info('port not defined. Shutting down server')
    elif not init_result:
        logger.info('Schedule IDs are not unique. Shutting down server')
    else:
        logger.info('Starting initial scheduled tasks')
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())

        logger.info('Running flask app')
        flask.run(port=port)  # (debug=True)
