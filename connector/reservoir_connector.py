import logging
from math import floor
import requests
from typing import Optional

from service import reservoir_service


logger = logging.getLogger('aquarium.reservoir_connector')


def register_with_system():
    url = f'{reservoir_service.system_host}/reservoirs/{reservoir_service.id}/register'
    logger.info(f'Attempting to register with url: {url}')
    try:
        response = requests.put(url)
    except OSError:
        logger.info(f'Connection refused. System not found')
    else:
        if response is None or floor(response.status_code / 100) != 2:
            logger.info(f'response: {response}')
        else:
            logger.info(f'Success: {response}')
            reservoir_service.change_status(reservoir_service.ReservoirStatus.ACTIVE)


def system_health_check(reservoir_id: str):
    url = f'{reservoir_service.system_host}/reservoirs/{reservoir_id}/health-check'
    logger.info(f'Running system health check with url: {url}')
    response: Optional[requests.Response] = None
    try:
        response = requests.get(url)
    except OSError:
        logger.info('Connection refused. System not found')
    finally:
        if response is None or floor(response.status_code / 100) != 2:
            logger.info(f'response: {response}')
            if reservoir_service.status != reservoir_service.ReservoirStatus.REGISTERING:
                reservoir_service.change_status(reservoir_service.ReservoirStatus.REGISTERING)
