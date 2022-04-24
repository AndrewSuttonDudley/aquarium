import logging
from math import floor
from typing import Optional
import requests
import sys

from service import system_service


logger = logging.getLogger('aquarium.reservoir_connector')


def health_check(_reservoir_id: str) -> bool:
    _reservoir = system_service.reservoirs[_reservoir_id]
    _url = f'{_reservoir.host}/health-check'
    logger.info(f'Checking health of {_reservoir.name} at url: {_url}')
    _response: Optional[requests.Response] = None
    try:
        _response = requests.get(_url)
    except OSError:
        logger.info(f'Reservoir not found. Unregistering {_reservoir.name}')
        return False
    finally:
        if _response is not None and floor(_response.status_code / 100) == 2:
            logger.info(f'{_reservoir.name} is healthy')
            return True

        logger.info(f'_response: {_response}')
        return False


def level_check(_reservoir_id: str) -> int:
    logger.info(f'Running level check for reservoir id: {_reservoir_id}')
    _reservoir = system_service.reservoirs[_reservoir_id]
    _url = f'{_reservoir.host}/level-check'
    logger.info(f'Getting level for reservoir (id: {_reservoir_id}) at url: {_url}')
    _response: Optional[requests.Response] = None
    try:
        _response = requests.get(_url)
    except OSError:
        logger.info(f'Reservoir not found')
    finally:
        if _response is not None and floor(_response.status_code / 100) == 2:
            logger.info(f'_response: {_response}')
            logger.info(f'_response.content: {_response.content}')
            return int(_response.content.decode("utf-8"))
    raise RuntimeError(f'Error retrieving water level for reservoir (id: {_reservoir_id})')
