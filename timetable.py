from timetable_unit import Schedule ,Event 

# CAN COMBINE OTHER TIMETABLE
# ADD SCHEDULE BUT WILL NOT LOOP
# CAN IDENTIFY PARTICULAR SCHEDULE CRASHED WITH WHICH SHECULE

class Timetable:
    def __init__(self):
        self._schedules: list[Schedule] = []
        self._added_timetable: list[Schedule] = []
        self._cycle: int = 7
        self._loop: int = 1
        self._overlap_indexes: set = set()
         
    def add_schedule(self ,value: int , start: str ,end: str ,event: Event):
        schedule = Schedule(value ,start ,end ,event)
        self._schedules.append(schedule)
        self._schedules.sort(key=lambda x: (x.start ,x.week_id))

    def set_cycle(self ,cycle: int):
        if(cycle != 0):
            self._cycle = cycle
        else:
            print("Cycle cannot be zero")

    def set_loop(self ,loop: int):
        self._loop = loop
    
    def get_schedules(self) -> list[Schedule]:
        array = []
        for i in range(self._loop):
            for j in self._schedules:
                array.append(
                    Schedule(
                    j._week_id + i * self._cycle,
                    j.start,
                    j.end,
                    j.event
                            ))
        return array
    
    def get_cycle_at(self ,schedule: Schedule) -> int:
         value = (schedule.week_id - 1) // self._cycle
         return value + 1
    
    def get_time_crashed_at(self) -> set[int]:
        crashed: set[int] = set()
        base_crashed: set[int] = set()
        length = len(self._schedules)

        for i in range(length - 1):
            if(self._schedules[i + 1].is_overlap(self._schedules[i])):
                base_crashed.update({i, i + 1})
    
        for j in range(self._loop):
            offset = length * j
            crashed.update({idx + offset for idx in base_crashed})
        
        return crashed
    
    # def overlap_at(self ,schedule: Schedule) -> set:
    #     s: set = set()
 
    schedules = property(get_schedules)

from event_collector import EventCollector 

EventCollector.add_event(Event("Kimia"))
EventCollector.add_event(Event("Physhic"))
EventCollector.add_event(Event("Biology"))

timetable1 = Timetable()
timetable1.set_loop(4)
timetable1.add_schedule(1 ,11.20 , 12.00 , EventCollector.get_event()[0])
timetable1.add_schedule(1 ,11.10 , 12.00 ,EventCollector.get_event()[1])

# timetable1.add_schedule(1 ,10.00 , 11.10 , EventCollector.get_event()[0])
# timetable1.add_schedule(49 ,11.20 , 12.00 , EventCollector.get_event()[2])
# timetable1.add_schedule(49 ,11.20 , 12.00 ,EventCollector.get_event()[0])
# timetable1.add_schedule(47 ,11.20 , 12.00 ,EventCollector.get_event()[1])

print(timetable1.get_time_crashed_at())
for j ,i in enumerate(timetable1.schedules):
    print("week " + str(timetable1.get_cycle_at(i)) ,str(i.start) + " to " + str(i.end) ,i.event.name ,end="") 
    # if(j in timetable1.get_time_crashed_at()):
    #     print(" crash" ,end="")
    print()
        
    