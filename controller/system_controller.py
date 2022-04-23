import http

from flask import Blueprint, json
import logging

from service import system_service


logger = logging.getLogger('aquarium.system_controller')

system_bp = Blueprint("system_blueprint", __name__)


@system_bp.route('/aquariums/<aquarium_id>/health-check', methods=['GET'])
def aquarium_health_check(aquarium_id: str):
    system_service.aquarium_health_check(aquarium_id)
    return '', http.HTTPStatus.NO_CONTENT


@system_bp.route('/aquariums/<aquarium_id>/register', methods=['PUT'])
def register_aquarium(aquarium_id: str):
    return json.dumps(system_service.register_aquarium(aquarium_id), default=vars)


@system_bp.route('/reservoirs/<reservoir_id>/health-check', methods=['GET'])
def reservoir_health_check(reservoir_id: str):
    system_service.reservoir_health_check(reservoir_id)
    return '', http.HTTPStatus.NO_CONTENT


@system_bp.route('/reservoirs/<id>/register', methods=['PUT'])
def register_reservoir(id: str):
    return json.dumps(system_service.register_reservoir(id), default=vars)
