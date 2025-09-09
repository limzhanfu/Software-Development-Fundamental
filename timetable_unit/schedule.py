from .event import Event

class Schedule:
    def __init__(self ,day_start:int=1 ,day_end:int=1 ,time_start:float=0.0 ,time_end:float=0.0 ,event:Event=Event("Untitle")
                 ,loop:int=1 ,cycle:int=7):
        self._day_start: int = day_start
        self._day_end: int = day_end
        self._time_start: float = time_start
        self._time_end: float = time_end
        self._event: Event = event
        self._loop: int = loop
        self._cycle: int = cycle


    def get_day_start(self):
        return self._day_start

    def get_day_end(self):
        return self._day_end

    def set_day_start(self ,day_start: float):
        if(day_start <= self._time_end):
            self._day_start = day_start
        else:
            print("Day start cannot bigger than day end")
        
    def set_day_end(self ,day_end: float):
        if(day_end <= self._time_end):
            self._day_end = day_end
        else:
            print("Day end cannot bigger than day start")

    def get_time_start(self):
        return self._time_start
    
    def get_time_end(self):
        return self._time_end
    
    def set_time_start(self ,start: int):
        if(start <= self._time_end):
            self._time_start = start  
        else:
            print("Start period cannot bigger than end period")

    def set_time_end(self ,end: int):
        if(end >= self._time_start):
            self._time_end = end  
        else:
            print("End period cannot lesser than than start period")

    def get_event(self):
        return self._event
    
    def set_event(self ,event: Event):
        self._event = event
    
    def get_loop(self):
        return self._loop

    def set_loop(self ,loop: int):
        if(loop <= 0):
            self._loop = loop
        else:
            print("Loop cannot be zero")
        self._loop = loop

    def get_cycle(self):
        return self._cycle

    def set_cycle(self ,cycle: int):
        if(cycle <= 0):
            self._cycle = cycle
        else:
            print("Cycle cannot be zero")
    
    # GET SET
    #############################################################################################

    # def get_cycle_at(self ,schedule: Schedule) -> int:
    #     value = (schedule.week_id - 1) // self._cycle
    #     return value + 1
    
    def get_loop_schedules(self) -> list["Schedule"]:
        array = []
        for i in range(self._loop):
                array.append(
                    Schedule(
                    day_start=self._day_start + i * self._cycle,
                    day_end=self._day_end + i * self._cycle,
                    time_start=self._time_start,
                    time_end=self._time_end,
                    event=self._event
                            ))
        return array
    

    def is_overlap(self ,schedule: "Schedule") -> bool:
        return((schedule.start < self._time_end and self._time_start < schedule._end)  
        if (schedule.day_start <= self.day_end and self.day_start <= schedule.day_end) else False) 
    
    @staticmethod
    def sort(array: list["Schedule"]) -> None:
        array.sort(key=lambda x: (x.day_start ,x.day_end ,x._time_start ,x._time_end))
   
    day_start = property(get_day_start ,set_day_end)
    day_end = property(get_day_end ,get_day_end)
    time_start = property(get_time_start ,set_time_start)
    time_end = property(get_time_end ,set_time_end)
    event = property(get_event ,set_event)
    cycle = property(get_cycle ,set_cycle)
    loop = property(get_loop ,set_loop)    

