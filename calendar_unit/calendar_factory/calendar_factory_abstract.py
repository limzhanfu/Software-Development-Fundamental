from abc import ABC ,abstractmethod
from calendar_unit import Year ,Month

class CalendarFactory(ABC):
    
    @abstractmethod
    def create_year(self ,year: int) -> Year:
        pass
    
    @abstractmethod
    def create_months(self ,is_leap_year: bool = False) -> list[Month]:
        pass
    