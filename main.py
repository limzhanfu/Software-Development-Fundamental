from calendar_unit import GregorianFactory ,IslamicFactory
from _calendar import Calendar 


islamic_calendar = Calendar("Islamic Calendar" ,1446 ,IslamicFactory())
gregorian_calendar = Calendar("Gregorian Calendar" ,2025 ,GregorianFactory())

print(gregorian_calendar.name)
print(gregorian_calendar.to_string())


# from timetable_unit import Timetable ,Event ,EventCollector,EWeek

# meeting = Event("Meeting")

# EventCollector.add_event(meeting)

# timetable1 = Timetable()
# timetable1.add_schedule(EWeek.MONDAY,(11,40),(12,20),EventCollector.events[0])


