from flask import Blueprint
import logging

from service import aquarium_service


logger = logging.getLogger('aquarium.aquarium_controller')

aquarium_bp = Blueprint("aquarium_blueprint", __name__)


@aquarium_bp.route('/hello-world', methods=['GET'])
def hello_world():
    logger.info('Hello World!')
    return 'Hello World!'
