from enum import Enum
import logging
from typing import Optional

from component import ResourceType


logger = logging.getLogger('aquarium.valve')


class ValveStatus(Enum):
    closed = 'closed'
    open = 'open'


class Valve:

    id: Optional[str] = None
    resource_key: Optional[int] = None
    resource_type: Optional[ResourceType] = None

    def __init__(self, id: str, resource_key: int, resource_type: ResourceType):
        self.id = id
        self.resource_key = resource_key
        self.resource_type = resource_type

    def get_status(self) -> ValveStatus:
        # Todo: Get status from actual valve
        return ValveStatus.closed

    def print(self):
        print(f'SourceValve(id: {self.id}, resource_key: {self.resource_key})')

    def set_status(self, status: ValveStatus):
        # Todo: Set status of actual valve
        logger.info(f'Setting valve status to {status}')
