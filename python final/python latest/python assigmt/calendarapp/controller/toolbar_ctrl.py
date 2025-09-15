from ..views import CalendarSwitcher
import datetime
from ..views.view_interface import IView  

class ToolbarController:
    def __init__(self ,calendar_switcher: CalendarSwitcher ,calendar_state: "CalendarState"
                  ,views: IView):
        self.cal_switcher = calendar_switcher
        self.state = calendar_state
        self.views = views
        self.bus = EventBus()
          
        self.bus.on("switch_view", self.on_switch)
        self.bus.on("prev", self.on_prev)
        self.bus.on("next", self.on_next)

        # switcher button
        self.cal_switcher.add_button(text="Month", command=lambda: self.bus.emit("switch_view", "month"))
        self.cal_switcher.add_button(text="Week", command=lambda: self.bus.emit("switch_view", "week"))
        self.cal_switcher.add_button(text="Day", command=lambda: self.bus.emit("switch_view", "day"))

        self.cal_switcher.add_button(text="<", command=lambda: self.bus.emit("prev"))
        self.cal_switcher.add_button(text=">", command=lambda: self.bus.emit("next"))

        self.cal_switcher.render_btn()
        
        if(self.views):
            method = self.views["month"].get_method()
            method()

    def on_switch(self, mode):
        self.state.set_mode(mode)
        self.show_view()

    def on_prev(self):
        if(self.state.view_mode == "month"):
            self.state.shift_date(datetime.timedelta(days=-30))
        elif(self.state.view_mode == "week"):
            self.state.shift_date(datetime.timedelta(days=-7))
        elif(self.state.view_mode == "day"):
            self.state.shift_date(datetime.timedelta(days=-1))
        self.show_view()

    def on_next(self):
        if self.state.view_mode == "month":
            self.state.shift_date(datetime.timedelta(days=30))
        elif self.state.view_mode == "week":
            self.state.shift_date(datetime.timedelta(days=7))
        elif(self.state.view_mode == "day"):
            self.state.shift_date(datetime.timedelta(days=1))
        self.show_view()


    def show_view(self):
        view = self.views[self.state.view_mode]
        method = view.get_method()
        method()

class CalendarState:
    def __init__(self, today):
        self.date = today
        self.view_mode = "month" 

    def set_mode(self, mode):
        self.view_mode = mode

    def shift_date(self, delta):
        self.date += delta
    
    def get_date(self):
        return self.date

class EventBus:
    def __init__(self):
        self.listeners = {}

    def on(self, event, callback):
        self.listeners.setdefault(event, []).append(callback)

    def emit(self, event, *args, **kwargs):
        for cb in self.listeners.get(event, []):
            cb(*args, **kwargs)





