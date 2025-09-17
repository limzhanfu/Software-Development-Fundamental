import tkinter as tk
from tkinter import ttk, messagebox
from .views import View ,CalendarSwitcher ,MonthView ,WeekView ,DayView ,EventDialog
from .controller import *
import calendar, datetime
from .event import * 

    
DEFAULT_CATEGORIES = {
    "Class": "#4caf50",
    "Meeting": "#2196f3",
    "Appointment": "#ff9800",
    "Personal": "#9c27b0",
    "Other": "#607d8b"
}

class CalendarApp:
    def __init__(self, master):
        self.master = master
        self.categories = DEFAULT_CATEGORIES.copy()

        self.today = datetime.date.today()
        self.current_year = self.today.year
        self.current_month = self.today.month
        self.selected_date = self.today

        self.main_area = ttk.Frame(master)
        self.main_area.grid(row=0, column=0, sticky="nsew")  

        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)


        ensure_data_file()
        self.events = self.load_events()

        self.create_widgets()
        self.refresh_sidebar()

        self.view = View(self.main_area)
        self.cs = CalendarState(self.selected_date)
        self.ctrl = ToolbarController(
            CalendarSwitcher(self.main_area),
            self.cs,
            {
                "month": MonthView(self.view, self.cs ,self),
                "week": WeekView(self.view, self.cs ,self),
                "day": DayView(self.view, self.cs ,self),
            }
        )

        self.ed = EventDialog(self ,categories=self.categories)

    # --- load/save using TXT format (one base64-encoded event per line) ---
    def load_events(self):
        events = []
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                for ln in f:
                    ln = ln.strip()
                    if not ln:
                        continue
                    ev = Event.from_line(ln)
                    if ev:
                        events.append(ev)
            return events
        except Exception as e:
            print("Failed loading events:", e)
            return []

    def save_events(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                for e in self.events:
                    f.write(e.to_line() + "\n")
        except Exception as e:
            messagebox.showerror("Save error", str(e))

    def create_widgets(self):
        self.master.grid_rowconfigure(0, weight=1)   
        self.master.grid_columnconfigure(0, weight=1) 
        self.master.grid_columnconfigure(1, weight=0) 

        sidebar = ttk.Frame(self.master, width=240)
        sidebar.grid(row=0, column=1, sticky="ns")  

        ttk.Label(sidebar, text="Events on selected day:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.NW, padx=8, pady=(8,0))
        self.event_listbox = tk.Listbox(sidebar, height=12)
        self.event_listbox.pack(fill=tk.X, padx=8, pady=6)
        self.event_listbox.bind("<<ListboxSelect>>", self.on_event_select)

        btn_frame = ttk.Frame(sidebar)
        btn_frame.pack(padx=8, pady=4, fill=tk.X)
        ttk.Button(btn_frame, text="Add", command=self.add_event_dialog).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(btn_frame, text="Edit", command=self.edit_selected_event).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_selected_event).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8, padx=8)
        ttk.Label(sidebar, text="Categories:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.NW, padx=8)
        self.cat_frame = ttk.Frame(sidebar)
        self.cat_frame.pack(fill=tk.X, padx=8, pady=4)
        self.draw_categories()

    def draw_categories(self):
        for w in self.cat_frame.winfo_children():
            w.destroy()
        for cat, col in self.categories.items():
            f = ttk.Frame(self.cat_frame)
            f.pack(fill=tk.X, pady=2)
            c = tk.Canvas(f, width=16, height=12)
            c.create_rectangle(0,0,16,12, fill=col, outline="")
            c.pack(side=tk.LEFT)
            ttk.Label(f, text=cat).pack(side=tk.LEFT, padx=6)

   
    def select_date(self, date_obj):
        self.selected_date = date_obj
        self.refresh_sidebar()

    def refresh_sidebar(self):
        self.event_listbox.delete(0, tk.END)
        day_events = self.get_day_events()
        for e in day_events:
            disp = f"{e.start+' ' if e.start else ''}{e.title} [{e.category}]"
            self.event_listbox.insert(tk.END, disp)
        if not day_events:
            self.event_listbox.insert(tk.END, "(No events)")


    def on_event_select(self, ev):
        sel = self.event_listbox.curselection()
        if not sel: return
        idx = sel[0]
        d = self.selected_date.isoformat()
        day_events = sorted([e for e in self.events if e.date==d], key=lambda x: x.start or "")
        if not day_events: return
        if idx >= len(day_events): return
        self.ed.show(event=day_events[idx])

    def add_event_dialog(self):
        date_str = self.selected_date.isoformat() if isinstance(self.selected_date, datetime.date) else datetime.date.today().isoformat()
        self.ed.show(None, default_date=date_str)

    def edit_selected_event(self):
        sel = self.event_listbox.curselection()
        if not sel: return
        idx = sel[0]
        d = self.selected_date.isoformat()
        day_events = sorted([e for e in self.events if e.date==d], key=lambda x: x.start or "")
        if not day_events: return
        if idx >= len(day_events): return
        self.ed.show(day_events[idx])

    def delete_selected_event(self):
        sel = self.event_listbox.curselection()
        if not sel: return
        idx = sel[0]
        d = self.selected_date.isoformat()
        day_events = sorted([e for e in self.events if e.date==d], key=lambda x: x.start or "")
        if not day_events: return
        if idx >= len(day_events): return
        ev = day_events[idx]
        if messagebox.askyesno("Delete", f"Delete event '{ev.title}'?"):
            self.events = [e for e in self.events if e.uid!=ev.uid]
            self.save_events()
            self.refresh_sidebar()
  
    def select_today(self):
        self.selected_date = datetime.date.today()
        self.refresh_sidebar()

    
    def get_day_events(self, date_obj=None):
        if date_obj is None:
            date_obj = self.selected_date

        if isinstance(date_obj, str):
            try:
                date_obj = datetime.date.fromisoformat(date_obj)
            except Exception:
                return []

        day_events = []
        for e in self.events:
            for occ in expand_occurrences(e):
                if occ == date_obj:   
                    day_events.append(e)
                    break
        return sorted(day_events, key=lambda x: x.start or "")


if __name__ == "__main__":
    root = tk.Tk()
    c  = CalendarApp(root)
    root.mainloop() 



