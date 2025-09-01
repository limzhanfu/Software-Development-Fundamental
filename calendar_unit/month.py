class Month :
    def __init__(self ,days: int ,name: str):
        self._days : int = days
        self._name : str = name

    def get_days(self):
        return self._days
    
    def get_name(self):
        return self._name 
    
    days = property(get_days)
    name = property(get_name)


