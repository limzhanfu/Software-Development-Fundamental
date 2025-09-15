import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry


class BookingView(ttk.Frame):
    BOOKINGS_FILE = "bookings.txt"
    SPLIT = "|"

    def __init__(self, master, username, full_name):
        super().__init__(master)
        self.username = username
        self.full_name = full_name
        self.rooms = {
            "Library": ["Room A (2-4 person)", "Room B (5-8 person)"],
            "Cyber Centre": ["Room A (4-6 person)", "Room B (5-8 person)"]
        }
        self._build()
        self._ensure_file()
        self._load_bookings()
        self._last_mtime = None  # file last modified time
        self._auto_refresh()

    def _ensure_file(self):
        if not os.path.exists(self.BOOKINGS_FILE):
            with open(self.BOOKINGS_FILE, "w", encoding="utf-8") as f:
                f.write("# username|venue|room|datetime|details\n")

    def _build(self):
        # Booking form
        form = ttk.LabelFrame(self, text="New Booking", padding=12)
        form.grid(row=0, column=0, sticky="ew", padx=12, pady=8)

        # Venue
        ttk.Label(form, text="Venue:").grid(row=0, column=0, sticky="w")
        self.venue_var = tk.StringVar()
        venue_cb = ttk.Combobox(
            form, textvariable=self.venue_var,
            values=["Library", "Cyber Centre"], state="readonly"
        )
        venue_cb.grid(row=0, column=1, sticky="ew", padx=4)
        venue_cb.current(0)

        # Room
        ttk.Label(form, text="Room:").grid(row=1, column=0, sticky="w")
        self.room_var = tk.StringVar()
        self.room_cb = ttk.Combobox(form, textvariable=self.room_var, state="readonly")
        self.room_cb.grid(row=1, column=1, sticky="ew", padx=4)

        # Date
        ttk.Label(form, text="Date:").grid(row=2, column=0, sticky="w")
        self.date_var = tk.StringVar()
        self.date_entry = DateEntry(form, textvariable=self.date_var, date_pattern="yyyy-mm-dd")
        self.date_entry.grid(row=2, column=1, sticky="ew", padx=4)

        # Start Time
        ttk.Label(form, text="Start Time:").grid(row=3, column=0, sticky="w")
        self.start_time_var = tk.StringVar()
        self.start_time_cb = ttk.Combobox(
            form, textvariable=self.start_time_var,
            values=[f"{h:02d}:00" for h in range(8, 23)], state="readonly"
        )
        self.start_time_cb.grid(row=3, column=1, sticky="ew", padx=4)
        self.start_time_cb.current(0)

        # End Time
        ttk.Label(form, text="End Time:").grid(row=4, column=0, sticky="w")
        self.end_time_var = tk.StringVar()
        self.end_time_cb = ttk.Combobox(
            form, textvariable=self.end_time_var,
            values=[f"{h:02d}:00" for h in range(8, 23)], state="readonly"
        )
        self.end_time_cb.grid(row=4, column=1, sticky="ew", padx=4)
        self.end_time_cb.current(1)

        # Details
        ttk.Label(form, text="Details:").grid(row=5, column=0, sticky="w")
        self.details_var = tk.StringVar()
        details_entry = ttk.Entry(form, textvariable=self.details_var, width=40)
        details_entry.grid(row=5, column=1, sticky="ew", padx=4)

        add_btn = ttk.Button(form, text="Add Booking", command=self._add_booking)
        add_btn.grid(row=6, column=0, columnspan=2, pady=8)
        
        check_btn = ttk.Button(form, text="Check Availability", command=self._check_availability)
        check_btn.grid(row=7, column=0, columnspan=2, pady=5)

        # Booking list
        list_frame = ttk.LabelFrame(self, text="My Bookings", padding=12)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=8)

        cols = ("venue", "datetime", "details")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=10)
        self.tree.heading("venue", text="Venue")
        self.tree.heading("datetime", text="Date & Time")
        self.tree.heading("details", text="Details")

        self.tree.column("venue", width=180, anchor="center")
        self.tree.column("datetime", width=200, anchor="center")
        self.tree.column("details", width=260)

        yscroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")

        # Cancel + Edit button
        btn_frame = ttk.Frame(list_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=(8, 0), sticky="ew")
        cancel_btn = ttk.Button(btn_frame, text="Cancel Booking", command=self._cancel_booking)
        cancel_btn.pack(side="left", expand=True, fill="x", padx=5)
        edit_btn = ttk.Button(btn_frame, text="Edit Booking", command=self._edit_booking)
        edit_btn.pack(side="left", expand=True, fill="x", padx=5)

        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        venue_cb.bind("<<ComboboxSelected>>", self._update_rooms)
        self._update_rooms()

    def _auto_refresh(self):
        if os.path.exists(self.BOOKINGS_FILE):
            mtime = os.path.getmtime(self.BOOKINGS_FILE)
            if self._last_mtime is None or mtime != self._last_mtime:
                self._last_mtime = mtime
                self._load_bookings()
        self.after(5000, self._auto_refresh)

    def _update_rooms(self, event=None):
        venue = self.venue_var.get()
        rooms = self.rooms.get(venue, [])
        self.room_cb["values"] = rooms
        if rooms:
            self.room_cb.current(0)

    def _add_booking(self):
        venue = self.venue_var.get().strip()
        room = self.room_var.get().strip()
        start_time = self.start_time_var.get().strip()
        end_time = self.end_time_var.get().strip()
        details = self.details_var.get().strip()

        if not venue or not room or not start_time or not end_time:
            messagebox.showwarning("Validation", "Please select venue, room and time range.")
            return

        if start_time >= end_time:
            messagebox.showerror("Validation", "End time must be later than start time.")
            return

        dt = f"{self.date_var.get()} {start_time}-{end_time}"

        if self._is_conflict(f"{venue} - {room}", dt):
            messagebox.showerror("Conflict", f"{venue} - {room} already booked at {dt}.")
            return

        line = f"{self.username}{self.SPLIT}{venue} - {room}{self.SPLIT}{dt}{self.SPLIT}{details}\n"
        with open(self.BOOKINGS_FILE, "a", encoding="utf-8") as f:
            f.write(line)

        self._load_bookings()
        messagebox.showinfo("Success", "Booking added successfully.")
        
    def _check_availability(self):
        venue = self.venue_var.get().strip()
        room = self.room_var.get().strip()
        start_time = self.start_time_var.get().strip()
        end_time = self.end_time_var.get().strip()
        date = self.date_var.get().strip()

        if not venue or not room or not start_time or not end_time:
            messagebox.showwarning("Check Availability", "Please select venue, room, and time.")
            return

        if start_time >= end_time:
            messagebox.showerror("Validation", "End time must be later than start time.")
            return

        dt = f"{date} {start_time}-{end_time}"
        venue_room = f"{venue} - {room}"

        # 🔧 Instead of showing error, always show table
        # If conflict found, still show table but do NOT stop user with popup
        conflict = self._is_conflict(venue_room, dt)
        self._show_availability_table(venue, room, date)            

    def _show_availability_table(self, venue, room, date):
        availability_window = tk.Toplevel(self)
        availability_window.title(f"Availability for {venue} - {room} on {date}")

        # ✅ Generate time ranges 08:00-09:00 ... 21:00-22:00
        time_slots = [f"{h:02d}:00-{h+1:02d}:00" for h in range(8, 22)]
        booked_slots = self._get_booked_slots(venue, room, date)

        table_frame = ttk.Frame(availability_window)
        table_frame.pack(padx=20, pady=20)

        ttk.Label(table_frame, text="Time Slot", width=20, anchor="center").grid(row=0, column=0, padx=4, pady=4)
        ttk.Label(table_frame, text="Availability", width=20, anchor="center").grid(row=0, column=1, padx=4, pady=4)

        for idx, time_slot in enumerate(time_slots):
            row = idx + 1
            ttk.Label(table_frame, text=time_slot, width=20, anchor="center").grid(row=row, column=0, padx=4, pady=4)
            start_hour = time_slot.split("-")[0]  # get start hour (e.g. "08:00")
            status = "Available" if start_hour not in booked_slots else "Booked"
            color = "lightgreen" if status == "Available" else "lightcoral"
            ttk.Label(table_frame, text=status, width=20, anchor="center", background=color).grid(row=row, column=1, padx=4, pady=4)

        close_button = ttk.Button(availability_window, text="Close", command=availability_window.destroy)
        close_button.pack(pady=10)



    def _get_booked_slots(self, venue, room, date):
        """Get the list of booked start times (e.g. '08:00', '09:00') for the given venue, room, and date."""
        booked_slots = set()
        if not os.path.exists(self.BOOKINGS_FILE):
            return booked_slots

        with open(self.BOOKINGS_FILE, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(self.SPLIT)
                if len(parts) < 4:
                    continue
                user, venue_room, dt, details = parts
                if venue_room == f"{venue} - {room}":
                    try:
                        booked_date, booked_time_range = dt.split()
                        if booked_date != date:
                            continue
                        booked_start, booked_end = booked_time_range.split("-")
                    except ValueError:
                        continue
                    for h in range(int(booked_start.split(":")[0]), int(booked_end.split(":")[0])):
                        booked_slots.add(f"{h:02d}:00")
        return booked_slots

    def _edit_booking(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Edit Booking", "Please select a booking to edit.")
            return

        values = self.tree.item(selected[0], "values")
        if len(values) < 3:
            messagebox.showerror("Edit Booking", "Selected booking has invalid data.")
            return

        old_venue_room, old_dt, old_details = values

        # split venue & room safely
        if " - " in old_venue_room:
            old_venue, old_room = old_venue_room.split(" - ", 1)
        else:
            old_venue, old_room = old_venue_room, ""

        # parse old date/time
        try:
            old_date, old_time_range = old_dt.split()
            old_start, old_end = old_time_range.split("-")
        except ValueError:
            messagebox.showerror("Edit Booking", "Selected booking has invalid date/time format.")
            return

        win = tk.Toplevel(self)
        win.title("Edit Booking")

        # Venue
        ttk.Label(win, text="Venue:").grid(row=0, column=0, padx=5, pady=5)
        venue_var = tk.StringVar(value=old_venue)
        venue_cb = ttk.Combobox(win, textvariable=venue_var,
                            values=list(self.rooms.keys()), state="readonly")
        venue_cb.grid(row=0, column=1, padx=5, pady=5)

        # Room
        ttk.Label(win, text="Room:").grid(row=1, column=0, padx=5, pady=5)
        room_var = tk.StringVar(value=old_room)
        rooms_for_old = self.rooms.get(old_venue, [])
        # ensure original room is selectable even if it's not in rooms list
        if old_room and old_room not in rooms_for_old:
            room_values = rooms_for_old + [old_room]
        else:
            room_values = rooms_for_old
        room_cb = ttk.Combobox(win, textvariable=room_var,
                            values=room_values, state="readonly")
        room_cb.grid(row=1, column=1, padx=5, pady=5)
        if old_room in room_values:
            room_cb.current(room_values.index(old_room))

        def update_rooms(event=None):
            venue = venue_var.get()
            rooms = self.rooms.get(venue, [])
            room_cb["values"] = rooms
            if rooms:
                room_cb.current(0)
                room_var.set(rooms[0])
            else:
                room_var.set("")

        venue_cb.bind("<<ComboboxSelected>>", update_rooms)

        # Date
        ttk.Label(win, text="Date:").grid(row=2, column=0, padx=5, pady=5)
        date_var = tk.StringVar(value=old_date)
        date_entry = DateEntry(win, textvariable=date_var, date_pattern="yyyy-mm-dd")
        date_entry.grid(row=2, column=1, padx=5, pady=5)

        # Start Time
        ttk.Label(win, text="Start Time:").grid(row=3, column=0, padx=5, pady=5)
        start_time_var = tk.StringVar(value=old_start)
        start_cb = ttk.Combobox(win, textvariable=start_time_var,
                            values=[f"{h:02d}:00" for h in range(8, 23)], state="readonly")
        start_cb.grid(row=3, column=1, padx=5, pady=5)

        # End Time
        ttk.Label(win, text="End Time:").grid(row=4, column=0, padx=5, pady=5)
        end_time_var = tk.StringVar(value=old_end)
        end_cb = ttk.Combobox(win, textvariable=end_time_var,
                            values=[f"{h:02d}:00" for h in range(8, 23)], state="readonly")
        end_cb.grid(row=4, column=1, padx=5, pady=5)

        # Details
        ttk.Label(win, text="Details:").grid(row=5, column=0, padx=5, pady=5)
        details_var = tk.StringVar(value=old_details)
        details_entry = ttk.Entry(win, textvariable=details_var, width=30)
        details_entry.grid(row=5, column=1, padx=5, pady=5)

        def save_changes():
            new_venue = venue_var.get().strip()
            new_room = room_var.get().strip()
            new_start = start_time_var.get().strip()
            new_end = end_time_var.get().strip()
            new_details = details_var.get().strip()

            if not new_venue or not new_room or not new_start or not new_end:
                messagebox.showwarning("Edit Booking", "Please fill venue, room and time.")
                return

            if new_start >= new_end:
                messagebox.showerror("Validation", "End time must be later than start time.")
                return

            new_dt = f"{date_var.get()} {new_start}-{new_end}"
            new_venue_room = f"{new_venue} - {new_room}"

            # Exclude the current booking from conflict check to avoid false positive
            exclude = (self.username, old_venue_room.strip(), old_dt.strip(), old_details.strip())
            if self._is_conflict(new_venue_room, new_dt, exclude=exclude):
                messagebox.showerror("Conflict", f"{new_venue_room} already booked at {new_dt}.")
                return

            # update file: use split(maxsplit=3) so details may contain '|'
            lines = []
            replaced = False
            with open(self.BOOKINGS_FILE, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.rstrip("\n")
                    if not line or line.startswith("#"):
                        lines.append(line)
                        continue
                    parts = line.split(self.SPLIT, 3)
                    if len(parts) < 4:
                        lines.append(line)
                        continue
                    user, v, d, det = [p.strip() for p in parts]
                    # match the original booking record (only replace the first matching one)
                    if (user == self.username and v == old_venue_room and d == old_dt and det == old_details and not replaced):
                        lines.append(f"{self.username}{self.SPLIT}{new_venue_room}{self.SPLIT}{new_dt}{self.SPLIT}{new_details}")
                        replaced = True
                    else:
                        lines.append(line)

            if not replaced:
                messagebox.showwarning("Edit Booking", "Original booking not found in file; no changes made.")
                return

            with open(self.BOOKINGS_FILE, "w", encoding="utf-8") as f:
                for l in lines:
                    f.write(l + "\n")

            self._load_bookings()
            win.destroy()
            messagebox.showinfo("Edit Booking", "Booking updated successfully.")

        ttk.Button(win, text="Save", command=save_changes).grid(row=6, column=0, columnspan=2, pady=10)


    def _is_conflict(self, venue_room, dt, exclude=None):
        """
    Check conflict by comparing same venue+room & overlapping time range.
    exclude: optional tuple (user, venue_room, dt, details) to ignore (useful when editing).
        """
        if not os.path.exists(self.BOOKINGS_FILE):
            return False

        try:
            new_date, new_time_range = dt.split()
            new_start, new_end = new_time_range.split("-")
        except ValueError:
            # invalid dt format -> treat as no conflict
            return False

        with open(self.BOOKINGS_FILE, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.rstrip("\n")
                if not line or line.startswith("#"):
                    continue

            # IMPORTANT: only split into 4 pieces so 'details' may contain '|' safely
                parts = line.split(self.SPLIT, 3)
                if len(parts) < 4:
                    continue

                user, booked_venue_room, booked_dt, booked_details = [p.strip() for p in parts]

            # if this is the record we're editing, skip it
                if exclude and (user, booked_venue_room, booked_dt, booked_details) == exclude:
                    continue

                if booked_venue_room != venue_room:
                    continue

                try:
                    booked_date, booked_time_range = booked_dt.split()
                    booked_start, booked_end = booked_time_range.split("-")
                except ValueError:
                    continue

                if booked_date == new_date:
                # overlap check: not (new_end <= booked_start or new_start >= booked_end)
                    if not (new_end <= booked_start or new_start >= booked_end):
                        return True
        return False


    def _cancel_booking(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cancel Booking", "Please select a booking to cancel.")
            return

        values = self.tree.item(selected[0], "values")
        venue_room, dt, details = values

        new_lines = []
        deleted = False
        with open(self.BOOKINGS_FILE, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    new_lines.append(line)
                    continue
                parts = line.split(self.SPLIT)
                if len(parts) < 4:
                    new_lines.append(line)
                    continue
                user, booked_venue_room, booked_dt, booked_details = parts
                if (user == self.username and booked_venue_room == venue_room and
                    booked_dt == dt and booked_details == details and not deleted):
                    deleted = True
                    continue
                new_lines.append(line)

        with open(self.BOOKINGS_FILE, "w", encoding="utf-8") as f:
            for line in new_lines:
                f.write(line + "\n")

        self._load_bookings()
        if deleted:
            messagebox.showinfo("Cancel Booking", "Booking cancelled successfully.")
        else:
            messagebox.showwarning("Cancel Booking", "Failed to cancel booking.")

    def _load_bookings(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not os.path.exists(self.BOOKINGS_FILE):
            return

        with open(self.BOOKINGS_FILE, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(self.SPLIT)
                if len(parts) < 4:
                    continue
                user, venue, dt, details = parts
                if user == self.username:
                    self.tree.insert("", "end", values=(venue, dt, details))
