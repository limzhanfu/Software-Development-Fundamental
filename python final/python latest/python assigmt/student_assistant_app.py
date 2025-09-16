import os
import tkinter as tk
from tkinter import ttk, messagebox

# --- Import your other modules ---
from booking import BookingView
from gpa import CgpaView
from report import ReportView
from calendarapp.app import CalendarApp 
from notes import NotesView

# --- Files ---
USERS_FILE = "users.txt"
COURSES_FILE = "courses.txt"
SPLIT = "|"

# --- Demo Data ---
DEMO_USERS = [
    # username|password|full_name
    "2401234|123456|Jason",
    "2401231|abc123|Han",
]

DEMO_COURSES = [
    # username|course_id|course_name|lecturer|schedule
    "2401234|AMCS1034|Software Development Fundamentals|Wong Wai Zhong|Mon 10:00–12:00, DK X",
    "2401234|AMCS2093|Operating System|Chua Chi Log|Wed 14:00–16:00, K103",
    "2401234|AMIT2033|Networking Essentials|Chaw Thim Vai|Tue 09:00–11:00, DK ABA",
    "2401234|AMIT2014|Web And Mobile Systems|Laiw Chun Voon|Thu 13:00–15:00, DK ABA",

    "2401231|ABDM2073|Organisational Behaviour|Suganthi A/P Magason|Mon 8:00-10:00, DK ABA",
    "2401231|ABDH2173|Introduction To Human Resource Management|Tin Shin Thed|Tue 12:00-14:00, DK D",
    "2401231|AMIS2723|Introduction To Business Analytics|Ong Mor Yang|Wed 9:00-11:00, DK C",
    "2401231|ABIS2703|MIS In The Digital Age|Loh Chuang Li|Thu 10:00-12:00, DK D",
]
class CalendarTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.app = CalendarApp(self)


# --- Helpers to create/load data ---
def ensure_demo_files():
    """Create demo text files on first run."""
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            for line in DEMO_USERS:
                f.write(line + "\n")

    if not os.path.exists(COURSES_FILE):
        with open(COURSES_FILE, "w", encoding="utf-8") as f:
            for line in DEMO_COURSES:
                f.write(line + "\n")


def load_users():
    users = {}
    if not os.path.exists(USERS_FILE):
        return users
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(SPLIT)
            if len(parts) < 3:
                continue
            username, password, full_name = parts[0], parts[1], parts[2]
            users[username] = {"password": password, "full_name": full_name}
    return users


def load_courses(username=None):
    courses = []
    if not os.path.exists(COURSES_FILE):
        return courses
    with open(COURSES_FILE, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(SPLIT)
            if len(parts) < 5:
                continue
            user, course_id, course_name, lecturer, schedule = [p.strip() for p in parts]
            if username is None or user == username:
                courses.append({
                    "id": course_id,
                    "name": course_name,
                    "lecturer": lecturer,
                    "schedule": schedule,
                })
    return courses


# --- Login Screen ---
class LoginFrame(ttk.Frame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.users = load_users()

        self.columnconfigure(0, weight=1)

        card = ttk.Frame(self, padding=24, style="Card.TFrame")
        card.grid(column=0, row=0, padx=24, pady=24, sticky="nsew")

        title = ttk.Label(card, text="Student Assistant App", style="Title.TLabel")
        subtitle = ttk.Label(card, text="Please sign in", style="Subtitle.TLabel")

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        user_label = ttk.Label(card, text="Username")
        user_entry = ttk.Entry(card, textvariable=self.username_var, width=30)
        pass_label = ttk.Label(card, text="Password")
        pass_entry = ttk.Entry(card, textvariable=self.password_var, width=30, show="•")

        login_btn = ttk.Button(card, text="Login", command=self.try_login, style="Accent.TButton")

        # Layout
        title.grid(column=0, row=0, sticky="w")
        subtitle.grid(column=0, row=1, pady=(0, 16), sticky="w")

        user_label.grid(column=0, row=2, sticky="w")
        user_entry.grid(column=0, row=3, pady=(0, 8), sticky="ew")

        pass_label.grid(column=0, row=4, sticky="w")
        pass_entry.grid(column=0, row=5, pady=(0, 16), sticky="ew")

        login_btn.grid(column=0, row=6, sticky="ew")

        # Bind Enter
        user_entry.bind("<Return>", lambda e: pass_entry.focus_set())
        pass_entry.bind("<Return>", lambda e: self.try_login())

        card.columnconfigure(0, weight=1)

    def try_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("Validation", "Please enter username and password.")
            return

        record = self.users.get(username)
        if not record or record["password"] != password:
            messagebox.showerror("Login Failed", "Invalid username or password.")
            return

        self.on_login_success(username, record["full_name"])


# --- Courses Tab ---
class CoursesView(ttk.Frame):
    def __init__(self, master, username):
        super().__init__(master)
        self.username = username
        self.tree = None
        self.build()

    def build(self):
        toolbar = ttk.Frame(self, padding=(0, 0, 0, 8))
        toolbar.grid(row=0, column=0, sticky="ew")
        refresh_btn = ttk.Button(toolbar, text="Refresh", command=self.populate)
        refresh_btn.pack(side="right")

        columns = ("id", "name", "lecturer", "schedule")
        tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        tree.heading("id", text="Course ID")
        tree.heading("name", text="Course Name")
        tree.heading("lecturer", text="Lecturer")
        tree.heading("schedule", text="Schedule")

        tree.column("id", width=100, anchor="center")
        tree.column("name", width=260)
        tree.column("lecturer", width=160)
        tree.column("schedule", width=220)

        yscroll = ttk.Scrollbar(self, orient="vertical", command=tree.yview)
        xscroll = ttk.Scrollbar(self, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        tree.grid(row=1, column=0, sticky="nsew")
        yscroll.grid(row=1, column=1, sticky="ns")
        xscroll.grid(row=2, column=0, sticky="ew")

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.tree = tree
        self.populate()

    def populate(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for c in load_courses(self.username):
            self.tree.insert("", "end", values=(c["id"], c["name"], c["lecturer"], c["schedule"]))


# --- Main App ---
class AppFrame(ttk.Frame):
    def __init__(self, master, username, full_name, on_logout):
        super().__init__(master)
        self.username = username
        self.full_name = full_name
        self.on_logout = on_logout

        header = ttk.Frame(self, padding=(16, 12, 16, 12), style="Header.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        title = ttk.Label(header, text="Student Assistant", style="HeaderTitle.TLabel")
        welcome = ttk.Label(header, text=f"Welcome, {self.full_name} ({self.username})", style="HeaderSub.TLabel")
        logout_btn = ttk.Button(header, text="Logout", command=self.on_logout)

        title.pack(side="left")
        welcome.pack(side="left", padx=(12, 0))
        logout_btn.pack(side="right")

        body = ttk.Notebook(self)
        body.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))

        courses_tab = CoursesView(body, self.username)
        body.add(courses_tab, text="My Courses")

        booking_tab = BookingView(body, self.username, self.full_name)
        body.add(booking_tab, text="Booking")

        gpa_tab = CgpaView(body, self.username, self.full_name)
        body.add(gpa_tab, text="GPA Calculator")

        report_tab = ReportView(body, self.username)
        body.add(report_tab, text="GPA Results")

        calendar_tab = CalendarTab(body)
        body.add(calendar_tab, text="Calendar")

        notes_tab = NotesView(body, self.username)
        body.add(notes_tab, text="Notes Organizer")


        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)


class StudentAssistantApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Assistant App")
        self.geometry("900x760")
        self.minsize(720, 480)

        ensure_demo_files()
        self._setup_style()

        self.current = None
        self.show_login()

    def clear_current(self):
        if self.current is not None:
            self.current.destroy()
            self.current = None

    def show_login(self):
        self.clear_current()
        frame = LoginFrame(self, on_login_success=self.show_app)
        frame.pack(fill="both", expand=True)
        self.current = frame

    def show_app(self, username, full_name):
        self.clear_current()
        frame = AppFrame(self, username, full_name, on_logout=self.show_login)
        frame.pack(fill="both", expand=True)
        self.current = frame

    def _setup_style(self):
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.style.configure("Card.TFrame", background="#ffffff", relief="flat")
        self.style.configure("Header.TFrame", background="#e6f0fa")
        self.style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), background="#ffffff", foreground="#003366")
        self.style.configure("Subtitle.TLabel", foreground="#666", background="#ffffff")
        self.style.configure("HeaderTitle.TLabel", font=("Segoe UI", 14, "bold"), background="#e6f0fa", foreground="#003366")
        self.style.configure("HeaderSub.TLabel", foreground="#003366", background="#e6f0fa")
        self.style.configure("Accent.TButton", padding=(8, 6), background="#0078d7", foreground="white")
        self.style.map("Accent.TButton", background=[("active", "#005a9e")])
        self.style.configure("Treeview.Heading", background="#0078d7", foreground="white", font=("Segoe UI", 10, "bold"))
        self.style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)


def main():
    app = StudentAssistantApp()
    app.mainloop()


if __name__ == "__main__":
    main()
