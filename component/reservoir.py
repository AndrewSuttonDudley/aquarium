class Reservoir:

    id = ""
    capacity = 0
    host = ""
    initialized = True
    name = ""
    registered = False
    tested = False

    def __init__(self, id, host):
        self.id = id
        self.host = host

    def print(self):
        print(f'Reservoir(_id: {self.id}, _capacity: {self.capacity}, name: {self.name})')

    def test(self):
        print(f'Confirming remote aquarium initialization for Reservoir(_id: {self.id})')
