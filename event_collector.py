from timetable_unit.event import Event

class EventCollector:
    events: list[Event] = []

    @classmethod
    def add_event(cls ,event: Event):
        cls.events.append(event)
    
    @classmethod
    def remove_event(cls ,name: str):
        cls.events.remove(name) 
    
    @classmethod
    def get_event(cls):
        return cls.events
    
