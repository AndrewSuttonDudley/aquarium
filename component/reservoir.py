class Reservoir:

    _id = ""
    _capacity = 0
    _host = ""
    _initialized = True
    _name = ""
    _tested = False

    def __init__(self, id, host):
        self._id = id
        self._host = host

    def print(self):
        print(f'Reservoir(_id: {self._id}, _capacity: {self._capacity}, name: {self._name})')

    def test(self):
        print(f'Confirming remote aquarium initialization for Reservoir(_id: {self._id})')
