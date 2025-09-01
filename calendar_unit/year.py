from .month import Month
class Year :
    def __init__ (self ,year: int ,is_leap_year: bool ,months: list[Month]):
        self.year: int = year
        self._is_leap_year: bool = is_leap_year
        self._months : list[Month] = months

    def get_months(self):
        return self._months
    
    def get_is_leap_year(self) -> bool:
        return self._is_leap_year
    
    def display(self):
        for i in self._months:
            print(i.name ,i.days)

    is_leap_year = property(get_is_leap_year)
    months = property(get_months)
    