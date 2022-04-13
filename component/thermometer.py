class Thermometer:

    _id = ""
    _resource_key = ""

    def __init__(self, id, resource_key):
        self._id = id
        self._resource_key = resource_key

    def print(self):
        print(f'Thermometer(_id: {self._id}, _resource_key: {self._resource_key})')
