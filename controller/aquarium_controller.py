import http

from flask import Blueprint
import logging

from service import aquarium_service


logger = logging.getLogger('aquarium.aquarium_controller')

aquarium_bp = Blueprint("aquarium_blueprint", __name__)


@aquarium_bp.route('/health-check', methods=['GET'])
def health_check():
    return '', http.HTTPStatus.NO_CONTENT


@aquarium_bp.route('/level-check', methods=['GET'])
def level_check():
    return aquarium_service.level_check()
