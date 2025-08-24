import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class RoomBookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Discussion Room Booking System")
        self.root.geometry("600x500")
        
        # Initialize data storage
        self.venues = ["Library", "Cyber Centre"]
        self.rooms = {
            "Library": ["Study Room A", "Study Room B", "Group Room"],
            "Cyber Centre": ["Lab 1", "Lab 2", "Conference Room"]
        }
        self.bookings = []
        
        # Create notebook for multi-page interface
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create frames
        self.booking_frame = ttk.Frame(self.notebook)
        self.view_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.booking_frame, text="Make Booking")
        self.notebook.add(self.view_frame, text="View Bookings")
        
        # Setup booking page
        self.setup_booking_page()
        # Setup view bookings page
        self.setup_view_page()

    def setup_booking_page(self):
        # Venue selection
        ttk.Label(self.booking_frame, text="Select Venue:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.venue_var = tk.StringVar()
        venue_combo = ttk.Combobox(self.booking_frame, textvariable=self.venue_var, values=self.venues, state="readonly")
        venue_combo.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        venue_combo.bind("<<ComboboxSelected>>", self.update_rooms)
        
        # Room selection
        ttk.Label(self.booking_frame, text="Select Room:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.room_var = tk.StringVar()
        self.room_combo = ttk.Combobox(self.booking_frame, textvariable=self.room_var, state="readonly")
        self.room_combo.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
        
        # Date selection
        ttk.Label(self.booking_frame, text="Select Date:").grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(self.booking_frame, textvariable=self.date_var)
        self.date_entry.grid(row=2, column=1, padx=10, pady=10, sticky='ew')
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Time slot selection
        ttk.Label(self.booking_frame, text="Time Slot:").grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.time_var = tk.StringVar()
        time_combo = ttk.Combobox(self.booking_frame, textvariable=self.time_var, state="readonly")
        time_combo['values'] = [f"{h}:00 - {h+1}:00" for h in range(8, 18)]
        time_combo.grid(row=3, column=1, padx=10, pady=10, sticky='ew')
        time_combo.current(0)
        
        # User details
        ttk.Label(self.booking_frame, text="Your Name:").grid(row=4, column=0, padx=10, pady=10, sticky='w')
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(self.booking_frame, textvariable=self.name_var)
        name_entry.grid(row=4, column=1, padx=10, pady=10, sticky='ew')
        
        ttk.Label(self.booking_frame, text="Contact Info:").grid(row=5, column=0, padx=10, pady=10, sticky='w')
        self.contact_var = tk.StringVar()
        contact_entry = ttk.Entry(self.booking_frame, textvariable=self.contact_var)
        contact_entry.grid(row=5, column=1, padx=10, pady=10, sticky='ew')
        
        # Buttons
        check_btn = ttk.Button(self.booking_frame, text="Check Availability", command=self.check_availability)
        check_btn.grid(row=6, column=0, padx=10, pady=20)
        
        book_btn = ttk.Button(self.booking_frame, text="Confirm Booking", command=self.make_booking)
        book_btn.grid(row=6, column=1, padx=10, pady=20)
        
        # Configure grid columns
        self.booking_frame.columnconfigure(1, weight=1)

    def setup_view_page(self):
        # Create treeview for bookings
        columns = ("id", "venue", "room", "date", "time", "name")
        self.bookings_tree = ttk.Treeview(
            self.view_frame, 
            columns=columns, 
            show="headings",
            selectmode="browse"
        )
        
        # Define headings
        self.bookings_tree.heading("id", text="ID")
        self.bookings_tree.heading("venue", text="Venue")
        self.bookings_tree.heading("room", text="Room")
        self.bookings_tree.heading("date", text="Date")
        self.bookings_tree.heading("time", text="Time Slot")
        self.bookings_tree.heading("name", text="Booked By")
        
        # Set column widths
        self.bookings_tree.column("id", width=50, anchor='center')
        self.bookings_tree.column("venue", width=100)
        self.bookings_tree.column("room", width=120)
        self.bookings_tree.column("date", width=100)
        self.bookings_tree.column("time", width=120)
        self.bookings_tree.column("name", width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.view_frame, orient="vertical", command=self.bookings_tree.yview)
        self.bookings_tree.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        self.bookings_tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Delete button
        delete_btn = ttk.Button(self.view_frame, text="Cancel Booking", command=self.cancel_booking)
        delete_btn.grid(row=1, column=0, pady=10)
        
        # Configure grid
        self.view_frame.rowconfigure(0, weight=1)
        self.view_frame.columnconfigure(0, weight=1)

    def update_rooms(self, event=None):
        venue = self.venue_var.get()
        if venue:
            self.room_combo['values'] = self.rooms[venue]
            self.room_combo.current(0)

    def check_availability(self):
        venue = self.venue_var.get()
        room = self.room_var.get()
        date = self.date_var.get()
        time_slot = self.time_var.get()
        
        if not all([venue, room, date, time_slot]):
            messagebox.showwarning("Missing Information", "Please fill all fields")
            return
        
        # Check for conflicting bookings
        conflict = any(
            b for b in self.bookings 
            if b['venue'] == venue 
            and b['room'] == room 
            and b['date'] == date 
            and b['time'] == time_slot
        )
        
        if conflict:
            messagebox.showinfo("Availability", "❌ This time slot is not available")
        else:
            messagebox.showinfo("Availability", "✅ This time slot is available")

    def make_booking(self):
        venue = self.venue_var.get()
        room = self.room_var.get()
        date = self.date_var.get()
        time_slot = self.time_var.get()
        name = self.name_var.get()
        contact = self.contact_var.get()
        
        if not all([venue, room, date, time_slot, name, contact]):
            messagebox.showwarning("Missing Information", "Please fill all fields")
            return
        
        # Create booking ID
        booking_id = len(self.bookings) + 1
        
        # Add to bookings
        self.bookings.append({
            "id": booking_id,
            "venue": venue,
            "room": room,
            "date": date,
            "time": time_slot,
            "name": name,
            "contact": contact
        })
        
        messagebox.showinfo("Success", "Booking confirmed!")
        self.clear_booking_form()
        self.update_bookings_view()
        self.notebook.select(1)  # Switch to view bookings tab

    def clear_booking_form(self):
        self.venue_var.set('')
        self.room_var.set('')
        self.name_var.set('')
        self.contact_var.set('')
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.time_var.set('8:00 - 9:00')

    def update_bookings_view(self):
        # Clear existing items
        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)
        
        # Add new bookings
        for booking in self.bookings:
            self.bookings_tree.insert(
                "", "end", 
                values=(
                    booking["id"],
                    booking["venue"],
                    booking["room"],
                    booking["date"],
                    booking["time"],
                    booking["name"]
                )
            )

    def cancel_booking(self):
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a booking to cancel")
            return
            
        booking_id = self.bookings_tree.item(selected, "values")[0]
        booking_id = int(booking_id)
        
        # Remove booking
        self.bookings = [b for b in self.bookings if b["id"] != booking_id]
        
        # Update view
        self.update_bookings_view()
        messagebox.showinfo("Cancelled", "Booking has been cancelled")

if __name__ == "__main__":
    root = tk.Tk()
    app = RoomBookingApp(root)
    root.mainloop()