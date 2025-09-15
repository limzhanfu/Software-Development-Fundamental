import calendar as c,datetime
import tkinter as tk
from .view import View 
from .view_interface import IView


class MonthView(IView):
    def __init__(self, view: View, state ,app):
        self.view = view
        self.state = state  
        self.app = app
        
    def get_days(self):
        return ""

    def get_name(self):
        return "Month"
    
    def get_method(self):
        return self.show_month_view

    def show_month_view(self):
        self.view.clear_main()

        
        selected_day = self.state.get_date()
        year, month = selected_day.year, selected_day.month

        self.view.month_label.config(text=f"{c.month_name[month]} {year}")

        grid = tk.Frame(self.view.main_frame)
        grid.pack(expand=True, fill=tk.BOTH)


        days_of_week = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        for j, day in enumerate(days_of_week):
            tk.Label(grid, text=day, font=("Segoe UI", 10, "bold")).grid(row=0, column=j, padx=2, pady=2)

        
        cal = c.Calendar(firstweekday=0)
        month_days = cal.monthdatescalendar(year, month)

        for i, week in enumerate(month_days):
            for j, day in enumerate(week):
                frame = tk.Frame(grid, relief=tk.RIDGE, borderwidth=1)
                frame.grid(row=i + 1, column=j, sticky="nsew")

                grid.grid_rowconfigure(i + 1, weight=1, minsize=80)
                grid.grid_columnconfigure(j, weight=1, minsize=120)

                lbl_day = tk.Label(
                    frame,
                    text=str(day.day),
                    font=("Segoe UI", 9, "bold" if day.month == month else "normal"),
                )
                lbl_day.pack(anchor="nw")

                lbl_day.bind("<Button-1>", lambda ev, d=day: self.select_date(d))

                self.render_event_preview(frame, day)  

    def render_event_preview(self, parent, day):
        events = self.app.get_day_events(day)
        max_display = 3  
        for e in events[:max_display]:
            text = f"{e.start+' ' if e.start else ''}{e.title or '(No title)'}"
            col = self.app.categories.get(e.category, "#999999")
            lbl_evt = tk.Label(parent, text=text, anchor="w",
                            font=("Segoe UI", 8), padx=2, pady=1,
                            bg=col, fg="white")
            lbl_evt.pack(fill=tk.X, padx=1, pady=1)

        if len(events) > max_display:
            more = tk.Label(parent, text=f"+{len(events)-max_display} more",
                            font=("Segoe UI", 7, "italic"), fg="gray")
            more.pack(anchor="w", padx=2)
        


    def select_date(self, date_obj):        
        self.app.selected_date = date_obj
        self.app.refresh_sidebar()
        self.app.ctrl.on_switch("day")


            

if __name__ == "__main__":
    root = tk.Tk()
    today = datetime.date.today()
    week = ["Monday" ,"Tuesday" ,"Wednesday" ,"Thursday" ,"Friday" ,"Saturday" ,"Sunday"]
    mv = MonthView(View(root) ,today.year ,today ,c.Calendar(firstweekday=6).monthdatescalendar(today.year ,today.month))

    mv.show_month_view()
    root.mainloop()



            




