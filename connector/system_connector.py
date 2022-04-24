import logging
from math import floor
import requests
from typing import Optional

from service import aquarium_service
from service import reservoir_service


logger = logging.getLogger('aquarium.system_connector')


def register_aquarium_with_system(_aquarium_id: str):
    _url = f'{aquarium_service.system_host}/aquariums/{_aquarium_id}/register'
    logger.info(f'Attempting to register with url: {_url}')
    _response: Optional[requests.Response] = None
    try:
        _response = requests.put(_url)
    except OSError:
        logger.info('Connection refused. System not found')
    finally:
        if _response is None or floor(_response.status_code / 100) != 2:
            logger.info(f'_response: {_response}')
        else:
            logger.info(f'Success: {_response}')
            aquarium_service.change_status(aquarium_service.AquariumStatus.active)


def aquarium_health_check(_aquarium_id: str):
    _url = f'{aquarium_service.system_host}/aquariums/{_aquarium_id}/health-check'
    logger.info(f'Running system health check with url: {_url}')
    _response: Optional[requests.Response] = None
    try:
        _response = requests.get(_url)
    except OSError:
        logger.info('Connection refused. System not found')
    finally:
        if _response is None or floor(_response.status_code / 100) != 2:
            logger.info(f'response: {_response}')
            if aquarium_service.status != aquarium_service.AquariumStatus.registering:
                aquarium_service.change_status(aquarium_service.AquariumStatus.registering)


def register_reservoir_with_system(_reservoir_id: str):
    _url = f'{reservoir_service.system_host}/reservoirs/{_reservoir_id}/register'
    logger.info(f'Attempting to register with url: {_url}')
    _response: Optional[requests.Response] = None
    try:
        _response = requests.put(_url)
    except OSError:
        logger.info(f'Connection refused. System not found')
    finally:
        if _response is None or floor(_response.status_code / 100) != 2:
            logger.info(f'response: {_response}')
        else:
            logger.info(f'Success: {_response}')
            reservoir_service.change_status(reservoir_service.ReservoirStatus.active)


def reservoir_health_check(_reservoir_id: str):
    _url = f'{reservoir_service.system_host}/reservoirs/{_reservoir_id}/health-check'
    logger.info(f'Running system health check with url: {_url}')
    _response: Optional[requests.Response] = None
    try:
        _response = requests.get(_url)
    except OSError:
        logger.info('Connection refused. System not found')
    finally:
        if _response is None or floor(_response.status_code / 100) != 2:
            logger.info(f'response: {_response}')
            if reservoir_service.status != reservoir_service.ReservoirStatus.registering:
                reservoir_service.change_status(reservoir_service.ReservoirStatus.registering)
