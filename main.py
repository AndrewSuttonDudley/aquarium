from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import os

from flask import Flask
import logging
# from kink import inject
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


@flask.route('/health', methods=['GET'])
def health():
    return 'healthy'


if __name__ == '__main__':
    server_role = os.environ.get('AQUARIUM_SERVER_ROLE')
    logger.info(f'server_role: {server_role}')

    scheduler = BackgroundScheduler()
    port = -1
    if server_role == 'aquarium':
        flask.register_blueprint(aquarium_bp, url_prefix='/aquarium')
        aquarium_service.initialize('config/aquarium1.config.json')
        port = aquarium_service.config['port']
        scheduler.add_job(func=aquarium_service.register_with_system, trigger='interval', seconds=6)

    elif server_role == 'reservoir':
        flask.register_blueprint(reservoir_bp, url_prefix='/reservoir')
        reservoir_service.initialize('config/reservoir.config.json')
        port = reservoir_service.config['port']

    elif server_role == 'system':
        flask.register_blueprint(system_bp, url_prefix='/system')
        system_service.initialize('config/system.config.json')
        port = system_service.config['port']
        scheduler.add_job(func=system_service.wait_for_servers_to_register, trigger='interval', seconds=5)

    else:
        raise 'Required environment variable AQUARIUM_SERVER_ROLE not found. Server not starting.'

    logger.info('Starting initial scheduled tasks')
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

    logger.info('Running flask app')
    flask.run(port=port)  # (debug=True)
