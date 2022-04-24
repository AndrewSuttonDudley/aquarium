import logging
from math import floor
from typing import Optional
import requests

from service import system_service


logger = logging.getLogger('aquarium.aquarium_connector')


def health_check(_aquarium_id: str) -> bool:
    _aquarium = system_service.aquariums[_aquarium_id]
    _url = f'{_aquarium.host}/health-check'
    logger.info(f'Checking health of {_aquarium.name} at url: {_url}')
    _response: Optional[requests.Response] = None
    try:
        _response = requests.get(_url)
    except OSError:
        logger.info(f'Aquarium not found. Unregistering {_aquarium.name}')
        return False
    finally:
        if _response is not None and floor(_response.status_code / 100) == 2:
            logger.info(f'{_aquarium.name} is healthy')
            return True

        logger.info(f'_response: {_response}')
        return False


def level_check(_aquarium_id: str) -> int:
    logger.info(f'Running level check for aquarium id: {_aquarium_id}')
    return 100
