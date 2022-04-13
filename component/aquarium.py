class Aquarium:

    id = ""
    capacity = 0
    host = ""
    initialized = False
    name = ""
    registered = False
    schedule = []
    tested = False

    def __init__(self, id, host):
        self.id = id
        self.host = host

    def print(self):
        print(f'Aquarium(_id: {self.id}, _capacity: {self.capacity}, name: {self.name})')
        for _schedule_item in self.schedule:
            print(f'    ScheduleItem(_id: {_schedule_item["action"]})')

    def test(self):
        print(f'Confirming remote aquarium initialization for Aquarium(_id: {self.id})')
