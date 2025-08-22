from calendar_unit import Year

class Calendar:
    def __init__(self ,name: str ,year):
        self._name: str = name
        self._year: Year  = year
    
    def display(self):
        print(self._name ,self._year.year)
        self._year.display()

    def get_name(self):
        return self._name
    
    name = property(get_name)