from calendar_unit import Year ,ICalendarFactory

class Calendar:
    def __init__(self ,name: str ,year ,factory: ICalendarFactory):
        self._name: str = name
        self._year: Year
        self._calendar_factory: ICalendarFactory = factory

        self._year = self._calendar_factory.create_year(year)
    
    def display(self):
        print(self._name ,self._year.year)
        self._year.display()

    def get_name(self):
        return self._name
    
    def set_name(self ,name):
        self._name = name
    
    def get_factory(self):
        return self._calendar_factory
    
    def set_factory(self ,factory):
        self._calendar_factory = factory

    name = property(get_name ,set_name)
    factory = property(get_factory ,set_factory)