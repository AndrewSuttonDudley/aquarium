import os

from flask import Flask
import logging
# from kink import inject
# from twilio.rest import Client

from controller.aquarium_controller import aquarium_bp
from controller.reservoir_controller import reservoir_bp
from controller.system_controller import system_bp
from service import aquarium_service
from service import resevoir_service
from service import system_service


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

    if server_role == 'aquarium':
        flask.register_blueprint(aquarium_bp, url_prefix='/aquarium')
        aquarium_service.initialize('config/aquarium1.config.json')

    elif server_role == 'reservoir':
        flask.register_blueprint(reservoir_bp, url_prefix='/reservoir')
        resevoir_service.initialize('config/reservoir.config.json')

    elif server_role == 'system':
        flask.register_blueprint(system_bp, url_prefix='/system')
        system_service.initialize('config/system.config.json')

    else:
        raise 'Required environment variable AQUARIUM_SERVER_ROLE not found. Server not starting.'

    flask.run(debug=True)
