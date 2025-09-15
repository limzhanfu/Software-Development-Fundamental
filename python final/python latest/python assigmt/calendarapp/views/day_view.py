import datetime ,calendar as c
from .view import View 
from .view_interface import IView
import tkinter as tk 
from tkinter import ttk

class DayView(IView):
     def __init__(self ,view: View ,cs ,app):
        self.view = view
        self.cs = cs
        self.app = app
     
     def get_days(self):
         return c.calendar.monthrange(self.cs.get_date().year, self.cs.get_date().month)[1]

     def get_name(self):
        return "Day"
     
     def get_method(self):
        return self.show_day_view

     def show_day_view(self):

        self.view.clear_main()
        
        d = self.cs.get_date()
        self.view.month_label.config(text=d.strftime("%A, %d %B %Y"))
        frame = ttk.Frame(self.view.main_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        
        ttk.Label(frame, text="Events:", font=("Segoe UI", 12, "bold")).pack(anchor="nw")

        day_events = self.app.get_day_events(d)  
        for e in day_events:
            self.render_event(frame, e)

     def render_event(self, parent, e):
        f = ttk.Frame(parent, relief=tk.GROOVE, borderwidth=1, padding=6)
        f.pack(fill=tk.X, pady=4)

        col = self.app.categories.get(e.category, "#999999")
        c = tk.Canvas(f, width=14, height=14)
        c.create_rectangle(0, 0, 14, 14, fill=col, outline="")
        c.pack(side=tk.LEFT, padx=4)

        txt = f"{e.start+' ' if e.start else ''}{e.title} [{e.category}]"
        if e.cycle > 0:
            txt += f" [Repeats every {e.cycle}d x{e.loop if e.loop!=-1 else '∞'}]"

        ttk.Label(f, text=txt, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Button(f, text="Edit", command=lambda ev=e: self.app.ed.show(ev ,None)).pack(side=tk.RIGHT)
        print("Checking event:", e.title, e.date, e.start, e.end)
         
        
     def select_date(self, date_obj):        
         self.app.selected_date = date_obj
         self.app.refresh_sidebar()




if __name__ == "__main__":
    root = tk.Tk()
    today = datetime.date.today()
    dv = DayView(View(root) ,today)
    dv.show_day_view()
    root.mainloop()


  
