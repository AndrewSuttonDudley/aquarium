from enum import Enum
import logging
from typing import Optional

from component import ResourceType


logger = logging.getLogger('aquarium.water_jet')


class WaterJetStatus(Enum):
    off = 'off'
    on = 'on'


class WaterJet:

    id: Optional[str] = None
    resource_key: Optional[int] = None
    resource_type: Optional[ResourceType] = None

    def __init__(self, id: str, resource_key: int, resource_type: ResourceType):
        self.id = id
        self.resource_key = resource_key
        self.resource_type = resource_type

    def get_status(self) -> WaterJetStatus:
        # Todo: Get status from actual water jet
        return WaterJetStatus.off

    def print(self):
        print(f'WaterJet(id: {self.id}, resource_key: {self.resource_key}, resource_type: {self.resource_type})')

    def set_status(self, status: WaterJetStatus):
        # Todo: Set status of actual water jet
        logger.info(f'Setting water jet status to {status}')
