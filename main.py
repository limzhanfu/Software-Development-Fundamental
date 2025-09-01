from calendar_unit import GregorianFactory ,IslamicFactory
from _calendar import Calendar 


islamic_calendar = Calendar("Islamic Calendar" ,1984 ,IslamicFactory())
gregorian_calendar = Calendar("Gregorian Calendar" ,2025 ,GregorianFactory())

islamic_calendar.display()
print()
gregorian_calendar.display()


