from enum import Enum

class EWeek(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    def to_string(self) -> str:
        match self:
            case EWeek.MONDAY:
                return "Monday"
            
            case EWeek.TUESDAY:
                return "Tuesday"
            
            case EWeek.WEDNESDAY:
                return "Wednesday"
            
            case EWeek.THURSDAY:
                return "Thursday"
            
            case EWeek.FRIDAY:
                return "Friday"
            
            case EWeek.SATURDAY:
                return "Saturday"
            
            case EWeek.SUNDAY:
                return "Sunday"
            