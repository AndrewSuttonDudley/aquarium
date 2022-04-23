import logging
from math import floor
import requests
from typing import Optional

from service import aquarium_service


logger = logging.getLogger('aquarium.aquarium_connector')


def register_with_system():
    url = f'{aquarium_service.system_host}/aquariums/{aquarium_service.id}/register'
    logger.info(f'Attempting to register with url: {url}')
    try:
        response = requests.put(url)
    except OSError:
        logger.info('Connection refused. System not found')
    else:
        if response is None or floor(response.status_code / 200) != 2:
            logger.info(f'response: {response}')
        else:
            logger.info(f'Success: {response}')
            aquarium_service.change_status(aquarium_service.AquariumStatus.ACTIVE)


def system_health_check(aquarium_id: str):
    url = f'{aquarium_service.system_host}/aquariums/{aquarium_id}/health_check'
    logger.info(f'Running system health check with url: {url}')
    response: Optional[requests.Response] = None
    try:
        response = requests.get(url)
    except OSError:
        logger.info('Connection refused. System not found')
    finally:
        if response is None or floor(response.status_code / 100) != 2:
            logger.info(f'response: {response}')
            if aquarium_service.status != aquarium_service.AquariumStatus.REGISTERING:
                aquarium_service.change_status(aquarium_service.AquariumStatus.REGISTERING)
