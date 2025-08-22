from calendar_unit import gregorian_factory ,islamic_factory
from _calendar import Calendar 

def main():
    factory1 = gregorian_factory.GregorianFactory()
    factory2 = islamic_factory.IslamicCalendar() 
    islamic_calendar = Calendar("Islamic Calendar" ,factory2.create_year(1445))
    gregorian_calendar = Calendar("Gregorian Calendar" ,factory1.create_year(1984))

    islamic_calendar.display()
    print()
    gregorian_calendar.display()

if __name__ == "__main__":
    main()

