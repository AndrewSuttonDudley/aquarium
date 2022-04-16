class Reservoir:

    id = ""
    capacity = 0
    host = ""
    initialized = True
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
        return f'Reservoir(id: {self.id}, capacity: {self.capacity}, name: {self.name})'
