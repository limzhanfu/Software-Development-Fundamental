class Time:
    WHOLE_DAY_HOUR: int = 24
    WHOLE_DAY_MINUTE: int = 60    
    
    @classmethod
    def get_period(cls ,hour: int ,minute: int) -> float:
        if(Time.compare(param=hour ,lower=0 ,upper=cls.WHOLE_DAY_HOUR) and
           Time.compare(param=minute ,lower=0 ,upper=cls.WHOLE_DAY_MINUTE)):
            return float(hour) + float(minute) / 100
        else:
            return 0.0            
        
    @staticmethod
    def compare(param ,lower ,upper) -> bool:
        return lower < param < upper
    

    