from typing import Optional


class Thermometer:

    id: Optional[str] = None
    resource_key: Optional[int] = None
    resource_type: Optional[str] = None

    def __init__(self, id: str, resource_key: int, resource_type: str):
        self.id = id
        self.resource_key = resource_key
        self.resource_type = resource_type

    def get_temperature(self):
        # Todo: Get temperature from actual sensor
        return 70

    def print(self):
        print(f'Thermometer(id: {self.id}, resource_key: {self.resource_key}, resource_type: {self.resource_type})')
