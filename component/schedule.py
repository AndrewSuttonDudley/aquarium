class Schedule:

    id = ""
    type = ""
    cron = ""

    def __init__(self, id, type, cron):
        self.id = id
        self.type = type
        self.cron = cron

    def to_string(self):
        return f'Schedule(id: {self.id}, type: {self.type}, cron: {self.cron})'
