from enum import Enum

class EIslamicCalendar(Enum):
    MUHARRAM = 0
    SAFAR = 1
    RABIAL_AWWAL= 2
    RABIAL_THANI = 3
    JUMADA_AL_AWWAL = 4
    JUMADA_AL_THANI = 5
    RAJAB = 6
    SHA_BAN = 7
    RAMADAN = 8
    SHAWWAL = 9
    DHU_AL_QADAH = 10
    DHU_AL_HIJJAH = 11

    def to_string(self) -> str:
        match self:
            case EIslamicCalendar.MUHARRAM :
                return "Muharram"
            case EIslamicCalendar.SAFAR:
                return "Safar"
            case EIslamicCalendar.RABIAL_AWWAL:
                return "Rabi' al-Awwal"
            case EIslamicCalendar.RABIAL_THANI:
                return "Rabi' al-Thani"
            case EIslamicCalendar.JUMADA_AL_AWWAL:
                return "Jumada al-Awwal"
            case EIslamicCalendar.JUMADA_AL_THANI:
                return "Jumada al-Thani"
            case EIslamicCalendar.RAJAB:
                return "Rajab"
            case EIslamicCalendar.SHA_BAN:
                return "Sha'ban"
            case EIslamicCalendar.RAMADAN:
                return "Ramadan"
            case EIslamicCalendar.SHAWWAL:
                return "Shawwal"
            case EIslamicCalendar.DHU_AL_QADAH:
                return "Dhu al-Qadah"
            case EIslamicCalendar.DHU_AL_HIJJAH:
                return "Dhu al-Hijjah"



    




