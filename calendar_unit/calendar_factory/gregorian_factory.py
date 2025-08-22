from calendar_unit import Month ,Year
from ..calendar_enum.gregorian_calendar_emum import EGregorianCalendar as G
from .calendar_factory_abstract import CalendarFactory

class GregorianFactory(CalendarFactory):
    
    def create_year(self ,year: int) -> Year:
        is_leap_year = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
        return Year(year ,is_leap_year ,self.create_months(is_leap_year))
            
    def create_months(self ,is_leap_year: bool = False) -> list[Month]:
        months: list[Month] = []   

        for i in G:
            if i in (G.APRIL ,G.JUNE ,G.SEPTEMBER ,G.NOVEMBER):
                days = 30
            elif i == G.FEBRUARY:
                days = 29 if (not is_leap_year) else 28
            else:
                days = 31
            
            months.append(Month(days ,i.name))
        
        return months
    
    
