from flask import Blueprint
import logging

from service import reservoir_service


reservoir_bp = Blueprint('reservoir_blueprint', __name__)

logger = logging.getLogger('aquarium.reservoir_controller')


@reservoir_bp.route('/health-check', methods=['GET'])
def health_check():
    return 'Healthy'


@reservoir_bp.route('/hello-world', methods=['GET'])
def hello_world():
    logger.info('Hello World!')
    return 'Hello World!'
