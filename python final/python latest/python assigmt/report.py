import tkinter as tk
from tkinter import ttk, messagebox
import os
import matplotlib.pyplot as plt

RESULTS_FILE = "gpa_results.txt"
SPLIT = "|"


class ReportView(ttk.Frame):
    def __init__(self, master, username):
        super().__init__(master)
        self.username = username
        self.tree = None
        self.build()

    def build(self):
        ttk.Label(self, text="My GPA Results", font=("Segoe UI", 14, "bold")).pack(pady=10)

        # Table
        columns = ("course", "grade", "credit", "point")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        self.tree.heading("course", text="Course")
        self.tree.heading("grade", text="Grade")
        self.tree.heading("credit", text="Credit Hours")
        self.tree.heading("point", text="Grade Point")

        self.tree.column("course", width=200)
        self.tree.column("grade", width=80, anchor="center")
        self.tree.column("credit", width=100, anchor="center")
        self.tree.column("point", width=100, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Footer Label
        self.cgpa_label = ttk.Label(self, text="CGPA: N/A", font=("Segoe UI", 12, "bold"), foreground="blue")
        self.cgpa_label.pack(pady=5)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Refresh", command=self.populate).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Show Graph", command=self.show_graph).pack(side="left", padx=5)

        self.populate()

    def populate(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if not os.path.exists(RESULTS_FILE):
            self.cgpa_label.config(text="CGPA: N/A")
            return

        total_points = 0
        total_credits = 0

        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            for raw in f:
                parts = raw.strip().split(SPLIT)
                if len(parts) < 6:
                    continue
                user, course_id, course_name, grade, credit, point = parts
                if user == self.username:
                    self.tree.insert("", "end", values=(course_name, grade, credit, point))

                    try:
                        credit = float(credit)
                        point = float(point)
                    except ValueError:
                        continue

                    total_credits += credit
                    total_points += point * credit

        # Show CGPA
        if total_credits > 0:
            cgpa = round(total_points / total_credits, 2)
            self.cgpa_label.config(text=f"CGPA: {cgpa}")
        else:
            self.cgpa_label.config(text="CGPA: N/A")

    def show_graph(self):
        if not os.path.exists(RESULTS_FILE):
            messagebox.showinfo("No Data", "No GPA results found.")
            return

        attempts = []
        gpas = []
        total_points = 0
        total_credits = 0

        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            for raw in f:
                parts = raw.strip().split(SPLIT)
                if len(parts) < 6:
                    continue
                user, course_id, course_name, grade, credit, point = parts
                if user == self.username:
                    try:
                        credit = float(credit)
                        point = float(point)
                    except ValueError:
                        continue

                    total_points += point * credit
                    total_credits += credit
                    if total_credits > 0:
                        cgpa = total_points / total_credits
                        attempts.append(len(attempts) + 1)
                        gpas.append(round(cgpa, 2))

        if not gpas:
            messagebox.showinfo("No Data", "No GPA records for this user.")
            return

        plt.figure(figsize=(6, 4))
        plt.plot(attempts, gpas, marker="o", label="CGPA")
        plt.axhline(y=2.0, color="r", linestyle="--", label="Passing Line (2.0)")
        plt.title("CGPA Performance")
        plt.xlabel("Attempt")
        plt.ylabel("CGPA")
        plt.legend()
        plt.grid(True)
        plt.savefig("cgpa_chart.png")
        plt.show()
        messagebox.showinfo("Saved", "Graph saved as cgpa_chart.png")
