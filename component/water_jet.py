class WaterJet:

    _id = ""
    _resource_key = ""

    def __init__(self, id, resource_key):
        self._id = id
        self._resource_key = resource_key

    def print(self):
        print(f'WaterJet(_id: {self._id}, _resource_key: {self._resource_key})')
