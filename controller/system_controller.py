from flask import Blueprint, json
import logging

from service import system_service


logger = logging.getLogger('aquarium.system_controller')

system_bp = Blueprint("system_blueprint", __name__)


@system_bp.route('/aquariums/<id>/register', methods=['PUT'])
def register_aquarium(id: str):
    return json.dumps(system_service.register_aquarium(id), default=vars)


@system_bp.route('/reservoirs/<id>/register', methods=['PUT'])
def register_reservoir(id: str):
    return json.dumps(system_service.register_reservoir(id), default=vars)
