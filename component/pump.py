from enum import Enum
import logging
from typing import Optional

from component import ResourceType


logger = logging.getLogger('aquarium.pump')


class PumpStatus(Enum):
    off = 'off'
    on = 'on'


class Pump:

    id: Optional[str] = None
    resource_key: Optional[int] = None
    resource_type: Optional[ResourceType] = None

    def __init__(self, id: str, resource_key: int, resource_type: ResourceType):
        self.id = id
        self.resource_key = resource_key
        self.resource_type = resource_type

    def get_status(self) -> PumpStatus:
        # Todo: Get status from actual pump
        return PumpStatus.off

    def print(self):
        print(f'Pump(id: {self.id}, resource_key: {self.resource_key}, resource_type: {self.resource_type})')

    def set_status(self, status: PumpStatus):
        logger.info(f'Setting pump (id: {self.id}) status to {status}')
        # Todo: Set the status of the actual pump
