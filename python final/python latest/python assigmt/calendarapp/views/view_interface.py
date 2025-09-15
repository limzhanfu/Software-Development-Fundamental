from abc import ABC ,abstractmethod

class IView(ABC):
    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_method(self):
        pass
    
  
    
    
        