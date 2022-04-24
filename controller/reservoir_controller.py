import http

from flask import Blueprint
import logging

from service import reservoir_service


reservoir_bp = Blueprint('reservoir_blueprint', __name__)

logger = logging.getLogger('aquarium.reservoir_controller')


@reservoir_bp.route('/health-check', methods=['GET'])
def health_check():
    return '', http.HTTPStatus.NO_CONTENT


@reservoir_bp.route('/level-check', methods=['GET'])
def level_check():
    return str(reservoir_service.level_check())
