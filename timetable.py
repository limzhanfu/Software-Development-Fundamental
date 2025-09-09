from timetable_unit import Schedule ,Event 

# CAN COMBINE OTHER TIMETABLE
# ADD SCHEDULE BUT WILL NOT LOOP
# CAN IDENTIFY PARTICULAR SCHEDULE CRASHED WITH WHICH SHECULE

class Timetable:
    def __init__(self):
        self._schedules: list[Schedule] = []
        self._overlap_indexes: set = set()
         
    def add_schedule(self ,schedule: Schedule):
        self._schedules.append(schedule)
        Schedule.sort(self._schedules)

    def get_schedules(self) -> list[Schedule]:
        array = []
        for i in self._schedules:
            for j in i.get_loop_schedules():
                array.append(j)
        
        Schedule.sort(array)
        return array
    
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
timetable1.add_schedule(Schedule(day_start=5 ,day_end=5 ,time_start=11.10 ,time_end=12.00 ,event=EventCollector.get_event()[1] ,loop=2))
timetable1.add_schedule(Schedule(day_start=2 ,day_end=2 ,time_start=11.10 ,time_end=12.00 ,event=EventCollector.get_event()[0]))

# timetable1.add_schedule(1 ,10.00 , 11.10 , EventCollector.get_event()[0])
# timetable1.add_schedule(49 ,11.20 , 12.00 , EventCollector.get_event()[2])
# timetable1.add_schedule(49 ,11.20 , 12.00 ,EventCollector.get_event()[0])
# timetable1.add_schedule(47 ,11.20 , 12.00 ,EventCollector.get_event()[1])

# for i in timetable1._schedules:
#     print(str(i.day_start)+ " to " +str(i.day_end) ,str(i.time_start) + " to " + str(i.time_end) ,i.event.name) 

for i in timetable1.get_schedules():
    print(str(i.day_start)+ " to " +str(i.day_end) ,str(i.time_start) + " to " + str(i.time_end) ,i.event.name) 
        
    