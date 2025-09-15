import tkinter as tk
from tkinter import ttk, messagebox
import os

RESULTS_FILE = "gpa_results.txt"
COURSES_FILE = "courses.txt"
SPLIT = "|"

GRADE_SCALE = {
    "A": 4.0, "A-": 3.75,
    "B+": 3.5, "B": 3.0, "B-": 2.75,
    "C+": 2.5, "C": 2.0,
    "F": 0.0
}


class CgpaView(ttk.Frame):
    def __init__(self, master, username, full_name):
        super().__init__(master)
        self.username = username
        self.full_name = full_name

        self.tree = None
        self.build()
        self.populate_courses()

    def build(self):
        ttk.Label(self, text="GPA Calculator", font=("Segoe UI", 14, "bold")).pack(pady=10)

        # --- Frame for course list ---
        box = ttk.LabelFrame(self, text="Courses")
        box.pack(padx=10, pady=10, fill="both", expand=True)

        columns = ("id", "name", "grade", "credit")
        self.tree = ttk.Treeview(box, columns=columns, show="headings", height=10)

        self.tree.heading("id", text="Course ID")
        self.tree.heading("name", text="Course Name")
        self.tree.heading("grade", text="Grade")
        self.tree.heading("credit", text="Credit Hours")

        self.tree.column("id", width=120, anchor="center")
        self.tree.column("name", width=200)
        self.tree.column("grade", width=100, anchor="center")
        self.tree.column("credit", width=100, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        # enable editing on double click
        self.tree.bind("<Double-1>", self.on_double_click)

        box.rowconfigure(0, weight=1)
        box.columnconfigure(0, weight=1)

        # --- Buttons ---
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Calculate GPA", command=self.calculate_gpa).pack(side="left", padx=5)


    def on_double_click(self, event):
        """Create an editable combobox in the clicked cell"""
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        if not row_id or not col_id:
            return

        x, y, width, height = self.tree.bbox(row_id, col_id)
        value = self.tree.set(row_id, col_id)

        # Decide options for grade or credit
        if col_id == "#3":  # grade column
            options = list(GRADE_SCALE.keys())
        elif col_id == "#4":  # credit column
            options = ["2.0", "3.0", "4.0"]
        else:
            return  # only grade/credit editable

        combo = ttk.Combobox(self.tree, values=options, state="readonly")
        combo.place(x=x, y=y, width=width, height=height)
        combo.set(value)

        def save_edit(event=None):
            self.tree.set(row_id, col_id, combo.get())
            combo.destroy()

        combo.bind("<<ComboboxSelected>>", save_edit)
        combo.focus_set()


    def populate_courses(self):
        self.tree.delete(*self.tree.get_children())
        if not os.path.exists(COURSES_FILE):
            return

        with open(COURSES_FILE, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(SPLIT)
                if len(parts) < 5:
                    continue
                user, course_id, course_name, lecturer, schedule = [p.strip() for p in parts]
                if user == self.username:
                    self.tree.insert("", "end", values=(course_id, course_name, "", ""))

    def set_grade(self):
        """Select a grade for highlighted row"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Row", "Please select a course first.")
            return

        win = tk.Toplevel(self)
        win.title("Select Grade")
        win.geometry("250x120")

        ttk.Label(win, text="Choose grade:").pack(pady=5)
        grade_var = tk.StringVar()
        grade_cb = ttk.Combobox(win, textvariable=grade_var, values=list(GRADE_SCALE.keys()), state="readonly")
        grade_cb.pack(pady=5)
        grade_cb.current(0)

        ttk.Button(win, text="OK", command=lambda: self.save_value(selected, "grade", grade_var.get(), win)).pack(pady=5)

    def set_credit(self):
        """Select credit hours for highlighted row"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Row", "Please select a course first.")
            return

        win = tk.Toplevel(self)
        win.title("Select Credit Hour")
        win.geometry("250x120")

        ttk.Label(win, text="Choose credit hour:").pack(pady=5)
        credit_var = tk.StringVar()
        credit_cb = ttk.Combobox(win, textvariable=credit_var, values=["2.0", "3.0", "4.0"], state="readonly")
        credit_cb.pack(pady=5)
        credit_cb.current(1)

        ttk.Button(win, text="OK", command=lambda: self.save_value(selected, "credit", credit_var.get(), win)).pack(pady=5)

    def save_value(self, selected, column, value, win):
        """Helper to save value to Treeview"""
        self.tree.set(selected, column, value)
        win.destroy()

    def calculate_gpa(self):
        total_points = 0
        total_credits = 0

        # Load existing results into memory
        existing = []
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line:
                        continue
                    parts = line.split(SPLIT)
                    if len(parts) >= 6:
                        existing.append(parts)

        # dictionary {(username, course_id): [user, id, name, grade, credit, gpa]}
        records = {(u, cid): parts for u, cid, *parts in [(r[0], r[1], *r[2:]) for r in existing]}

        # loop Treeview rows
        for child in self.tree.get_children():
            course_id, course_name, grade, credit = self.tree.item(child)["values"]

            if not grade or not credit:
                continue

            if grade not in GRADE_SCALE:
                messagebox.showerror("Error", f"Invalid grade {grade} for {course_name}")
                return

            try:
                credit = float(credit)
            except ValueError:
                messagebox.showerror("Error", f"Invalid credit {credit} for {course_name}")
                return

            gpa_value = GRADE_SCALE[grade]
            total_points += gpa_value * credit
            total_credits += credit

            # update or insert new record
            records[(self.username, course_id)] = [
                self.username, course_id, course_name, grade, str(credit), f"{gpa_value:.2f}"
            ]

        if total_credits == 0:
            messagebox.showinfo("Result", "No grades/credits entered.")
            return

        gpa = round(total_points / total_credits, 2)

        # write back updated results
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            for rec in records.values():
                f.write(SPLIT.join(rec) + "\n")

        messagebox.showinfo("GPA Result", f"Your GPA is {gpa}")
