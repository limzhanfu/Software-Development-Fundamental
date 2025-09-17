from tkinter import ttk ,messagebox 
import tkinter as tk ,datetime 
from ..event import Event

def to_date(obj):
        if isinstance(obj, datetime.date):  
            return obj
        if isinstance(obj, str):  
            try:
                return datetime.datetime.strptime(obj, "%Y-%m-%d").date()
            except ValueError:
                return datetime.date.today()
        return datetime.date.today()


class EventDialog:
    def __init__(self, app ,categories=None):
        self.app = app
        self.categories = categories

    def show(self ,event=None ,default_date=None ,):
        dlg = tk.Toplevel(self.app.master)
        dlg.transient(self.app.master)
        dlg.grab_set()
        dlg.title("Edit Event" if event else "Add Event")

        frm = ttk.Frame(dlg, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(frm, text="Title:").grid(row=0, column=0, sticky="w")
        title_var = tk.StringVar(value=event.title if event else "")
        ttk.Entry(frm, textvariable=title_var, width=40).grid(row=0, column=1, sticky="w")

            # Start datetime
        ttk.Label(frm, text="Start:").grid(row=1, column=0, sticky="w")
        self.start_picker = DateTimePicker(
            frm,
            date=to_date(event.date if event else default_date or datetime.date.today()),
            time=(event.start if event else "08:00")
        )
        self.start_picker.grid(row=1, column=1, sticky="w")

        # End datetime
        ttk.Label(frm, text="End:").grid(row=2, column=0, sticky="w")
        self.end_picker = DateTimePicker(
            frm,
            date=to_date(event.date if event else default_date or datetime.date.today()),
            time=(event.end if event else "09:00")
        )
        self.end_picker.grid(row=2, column=1, sticky="w")

        # Category
        ttk.Label(frm, text="Category:").grid(row=3, column=0, sticky="w")
        cat_var = tk.StringVar(value=(event.category if event else list(self.categories.keys())[0]))
        cat_box = ttk.Combobox(frm, textvariable=cat_var, values=list(self.categories.keys()), state="readonly")
        cat_box.grid(row=3, column=1, sticky="w")


        # Notes
        ttk.Label(frm, text="Notes:").grid(row=5, column=0, sticky="nw")
        notes_txt = tk.Text(frm, width=40, height=5)
        notes_txt.grid(row=5, column=1, sticky="w")
        if event:
            notes_txt.insert("1.0", event.notes)

        # Cycle
        ttk.Label(frm, text="Cycle:").grid(row=6, column=0, sticky="w")
        cycle_var = tk.StringVar(value=(str(event.cycle) if event else "0"))
        ttk.Entry(frm, textvariable=cycle_var, width=5).grid(row=6, column=1, sticky="w")

        # Loop
        ttk.Label(frm, text="Loop:").grid(row=7, column=0, sticky="w")
        loop_var = tk.StringVar(value=(str(event.loop) if event else "1"))
        ttk.Entry(frm, textvariable=loop_var, width=5).grid(row=7, column=1, sticky="w")

        # Save / Delete / Cancel
        def save_and_close():
            title = title_var.get().strip()
            if not title:   
                messagebox.showwarning("Missing", "Please provide a title.")
                return

            start_dt = self.start_picker.get_datetime()
            end_dt = self.end_picker.get_datetime()
            if end_dt < start_dt:
                messagebox.showwarning("Invalid", "End time cannot be before start time.")
                return

            if event:  
                event.title = title
                event.date = self.start_picker.get_date_str()
                event.start = self.start_picker.get_time_str()
                event.end = self.end_picker.get_time_str()
                event.category = cat_var.get()
                event.notes = notes_txt.get("1.0", "end").strip()
                event.cycle = int(cycle_var.get().strip() or 0)
                event.loop = int(loop_var.get().strip() or 1)
            else:  
                evd = Event(
                    title,
                    self.start_picker.get_date_str(),
                    self.start_picker.get_time_str(),
                    self.end_picker.get_time_str(),
                    cat_var.get(),
                    notes_txt.get("1.0", "end").strip(),
                    cycle=int(cycle_var.get().strip() or 0),
                    loop=int(loop_var.get().strip() or 1)
        )
                self.app.events.append(evd)

            self.app.save_events()
            dlg.destroy()
            self.app.refresh_sidebar()
            self.app.ctrl.on_switch(self.app.ctrl.state.view_mode)

        btns = ttk.Frame(frm)
        btns.grid(row=8, column=0, columnspan=2, pady=8)
        ttk.Button(btns, text="Save", command=save_and_close).pack(side=tk.LEFT, padx=4)

        if event:
            def delete_and_close():
                if event and event in self.app.events:
                    self.app.events.remove(event)  
                    self.app.save_events()
                dlg.destroy()
                self.app.refresh_sidebar()
                self.app.ctrl.on_switch(self.app.ctrl.state.view_mode)
                    
            ttk.Button(btns, text="Delete", command=delete_and_close).pack(side=tk.LEFT, padx=4)

        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side=tk.LEFT, padx=4)
       

class DateTimePicker(ttk.Frame):
    def __init__(self, master, date=None, time=None, **kwargs):
        super().__init__(master, **kwargs)

        if not date:
            date = datetime.date.today()
        if not time:
            time = "08:00"

        
        self.year_var = tk.StringVar(value=str(date.year))
        years = [str(y) for y in range(2000, 2101)]
        ttk.Combobox(self, textvariable=self.year_var, values=years, width=5, state="readonly").grid(row=0, column=0)

        
        self.month_var = tk.StringVar(value=f"{date.month:02d}")
        months = [f"{m:02d}" for m in range(1, 13)]
        ttk.Combobox(self, textvariable=self.month_var, values=months, width=3, state="readonly").grid(row=0, column=1)

        
        self.day_var = tk.StringVar(value=f"{date.day:02d}")
        self.day_box = ttk.Combobox(self, textvariable=self.day_var, width=3, state="readonly")
        self.day_box.grid(row=0, column=2)
        self.update_days()  
        self.month_var.trace_add("write", lambda *a: self.update_days())
        self.year_var.trace_add("write", lambda *a: self.update_days())


        hour, minute = map(int, time.split(":"))
        self.hour_var = tk.StringVar(value=f"{hour:02d}")
        hours = [f"{h:02d}" for h in range(24)]
        ttk.Combobox(self, textvariable=self.hour_var, values=hours, width=3, state="readonly").grid(row=0, column=3)

        
        self.minute_var = tk.StringVar(value=f"{minute:02d}")
        minutes = [f"{m:02d}" for m in range(0, 60)]
        ttk.Combobox(self, textvariable=self.minute_var, values=minutes, width=3, state="readonly").grid(row=0, column=4)

    def update_days(self):

        year = int(self.year_var.get())
        month = int(self.month_var.get())
        if month == 2:  
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                max_day = 29
            else:
                max_day = 28
        elif month in (4, 6, 9, 11):
            max_day = 30
        else:
            max_day = 31
        days = [f"{d:02d}" for d in range(1, max_day + 1)]
        self.day_box["values"] = days
        if self.day_var.get() not in days:
            self.day_var.set("01")

    def get_date_str(self):
        return f"{self.year_var.get()}-{self.month_var.get()}-{self.day_var.get()}"

    def get_time_str(self):
        return f"{self.hour_var.get()}:{self.minute_var.get()}"

    def get_datetime(self):
        return datetime.datetime.strptime(
            f"{self.get_date_str()} {self.get_time_str()}",
            "%Y-%m-%d %H:%M"
        )



