import datetime, calendar as c
from .view import View
from .view_interface import IView
import tkinter as tk
from tkinter import ttk
from ..event import expand_occurrences

class WeekView(IView):
    def __init__(self, view: View, cs ,app):
        self.view = view
        self.cs = cs
        self.cells = {}   
        self.app = app

    def get_method(self):
        return self.show_week_view
     
    def get_days(self):
        d = self.cs.get_date()
        return c.monthrange(d.year, d.month)[1]
     
    def get_name(self):
        return "Week View"

    def show_week_view(self):
        self.view.clear_main()

        start = self.cs.get_date() - datetime.timedelta(days=self.cs.get_date().weekday())
        days = [start + datetime.timedelta(days=i) for i in range(7)]

        self.view.month_label.config(text=f"Week of {days[0].isoformat()}")

        grid = ttk.Frame(self.view.main_frame)
        grid.pack(fill=tk.BOTH, expand=True)

        ttk.Label(grid, text="Time").grid(row=0, column=0, sticky="nsew")
        for c, d in enumerate(days):
            ttk.Label(
                grid,
                text=d.strftime("%a\n%d %b"),
                borderwidth=1
            ).grid(row=0, column=c+1, sticky="nsew")
            grid.columnconfigure(c+1, weight=1)

        for hour in range(8, 20):
            grid.rowconfigure(hour, weight=1)
            ttk.Label(grid, text=f"{hour}:00").grid(row=hour, column=0, sticky="nsew")
            for c, d in enumerate(days):
                cell = tk.Frame(grid, relief=tk.RIDGE, borderwidth=1, height=40)
                cell.grid(row=hour, column=c+1, sticky="nsew", padx=1, pady=1)
                self.cells[(d, hour)] = cell

        
        self.render_events(days)

    def render_events(self, days):
        for e in self.app.events:
            for occ in expand_occurrences(e):  
                if not isinstance(occ, datetime.date):
                    continue
                if occ not in days:
                    continue

                if e.start:
                    try:
                        shour, smin = map(int, e.start.split(":"))
                    except Exception:
                        shour, smin = 8, 0
                else:
                    shour, smin = 8, 0

                
                if e.end:
                    try:
                        ehour, emin = map(int, e.end.split(":"))
                    except Exception:
                        ehour, emin = shour + 1, 0
                else:
                    ehour, emin = shour + 1, 0


                for h in range(shour, ehour+1):
                    cell = self.cells.get((occ, h))
                    if not cell:
                        continue

                    b = tk.Button(
                        cell,
                        text=f"{e.start+' ' if e.start else ''}{e.title}",
                        anchor="w",
                        command=lambda ev=e: self.app.ed.show(ev ,None)
                    )
                    col = self.app.categories.get(e.category, "#999999")
                    b.configure(bg=col, fg="white", relief=tk.RAISED)
                    b.pack(fill=tk.X, padx=1, pady=1)
                   

