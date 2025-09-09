from .event import Event

class Schedule:
    def __init__(self ,id: int ,start: float ,end: float ,event: Event):
        self._week_id: int = id
        self._start: float = start
        self._end: float = end
        self._event: Event = event

        if(self.start >= self._end or self.end <= self._start):
            self._start = 0.0
            self._end = 0.0
            print("Start and End period crashed")

    def get_week_id(self):
        return self._week_id

    def set_week_id(self ,week_id: int):
        self._week_id = week_id

    def get_start(self):
        return self._start
    
    def get_end(self):
        return self._end
    
    def set_start(self ,start: int):
        if(start < self._end):
            self._start = start  
        else:
            print("Start period cannot bigger than or equal to end period")

    def set_end(self ,end: int):
        if(end > self._start):
            self._end = end  
        else:
            print("End period cannot lesser than than or equal to start period")

    def get_event(self):
        return self._event
    
    def is_overlap(self ,schedule) -> bool:
        return (schedule.start < self._end and self._start < schedule._end) if (self._week_id == schedule.week_id) else False
   
    week_id = property(get_week_id ,set_week_id)
    start = property(get_start ,set_start)
    end = property(get_end ,set_end)
    event = property(get_event)    

