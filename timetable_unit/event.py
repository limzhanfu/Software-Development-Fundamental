class Event:
    def __init__(self ,name):
        self._name: str = name
        self._content: str = "?"
    
    def set_content(self ,content):
        self._content = content

    def get_content(self):
        return self._content
    
    def get_name(self):
        return self._name
    
    name = property(get_name)
    content = property(get_content ,set_content)