class Aquarium:

    id = ""
    capacity = 0
    host = ""
    initialized = False
    name = ""
    registered = False
    schedules = []
    tested = False

    def __init__(self, id, capacity, host, name):
        self.id = id
        self.capacity = capacity
        self.host = host
        self.name = name

    def to_string(self):
        return f'Aquarium(id: {self.id}, capacity: {self.capacity}, host: {self.host}, name: {self.name})'
