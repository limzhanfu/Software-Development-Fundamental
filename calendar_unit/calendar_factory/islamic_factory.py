from calendar_unit import Month ,Year
from ..calendar_enum.islamic_calendar_enum import EIslamicCalendar as I
from .calendar_factory_interface import ICalendarFactory

class IslamicFactory(ICalendarFactory):
    def create_year(self ,year: int) -> Year:
        is_leap_year = (year % 30 in (2 ,5 ,7 ,10 ,13 ,16 ,18 ,21 ,24 ,26 ,29))

        return(Year(year ,is_leap_year ,self.create_months(is_leap_year)))

    def create_months(self ,is_leap_year: bool = False) -> list[Month]:
        months: list[Month] = []

        for i in I:
            if(i.value % 2 == 0):
                days = 30
            elif(i.value == 11):
                days = 29 if(is_leap_year) else 30
            else:
                days = 29
            
            months.append(Month(days ,i.to_string()))
        
        return months
    