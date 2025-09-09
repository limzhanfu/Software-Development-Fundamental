from .month import Month
class Year :
    def __init__ (self ,year: int ,is_leap_year: bool ,months: list[Month]):
        self._year: int = year
        self._is_leap_year: bool = is_leap_year
        self._months : list[Month] = months

    def get_months(self):
        return self._months
    
    def get_is_leap_year(self) -> bool:
        return self._is_leap_year
    
    def display(self):
        print("Leap year : ",self._is_leap_year)
        count = 0
        for i in self._months:
            print(i.name ,i.days)
            count += i.days
        print("Total days : " ,count)

    def to_string(self) -> list[list[str]]:
       array: list[list[str]]= []
       for i in self._months:
            array.append([str(j + 1) + "-" + str(i.name) + "-" + str(self._year) for j in range(i.days)]) 
       return array

    is_leap_year = property(get_is_leap_year)
    months = property(get_months)
    