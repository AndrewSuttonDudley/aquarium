from flask import Blueprint
import logging

from service import system_service


system_bp = Blueprint("system_blueprint", __name__)

logger = logging.getLogger('aquarium.system_controller')


@system_bp.route('/aquariums/<id>/register', methods=['PUT'])
def register_aquarium(id: str):
    system_service.register_aquarium(id)


@system_bp.route('/reservoirs/<id>/register', methods=['PUT'])
def register_reservoir(id: str):
    system_service.register_reservoir(id)


@system_bp.route('/hello-world', methods=['GET'])
def hello_world():
    logger.info('Hello World!')
    return 'Hello World!'
