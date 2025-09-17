# notes.py
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from datetime import datetime

# Constants for file paths and separators
NOTES_FILE = "notes.txt"          # File where all notes are stored
IMAGE_FOLDER = "notes_images"     # Folder to store uploaded images
SPLIT = "|"                       # Separator symbol for saving note fields

# Ensure image folder exists
os.makedirs(IMAGE_FOLDER, exist_ok=True)


class NotesView(ttk.Frame):
    def __init__(self, master, username):
        super().__init__(master)
        self.username = username
        self.notes = []
        # Load categories from user's file (if exists), otherwise use default categories
        self.categories = self.load_user_categories()

        # Variables linked with UI widgets
        self.category_var = tk.StringVar(value="All")
        self.search_var = tk.StringVar()
        self.sort_var = tk.StringVar(value="Date (newest)")

        # Keep image references for thumbnails to avoid GC
        self._thumb_refs = []
        # Mapping from Treeview item id (iid) to note dict for precise lookup
        self._iid_map = {}

        # Build GUI and load notes
        self.build()
        self.load_notes()

    @staticmethod
    def escape_field(text: str) -> str:
        """Replace '|' with a safe token before saving"""
        return text.replace("|", "[PIPE]")

    @staticmethod
    def unescape_field(text: str) -> str:
        """Restore '[PIPE]' back to '|' when reading"""
        return text.replace("[PIPE]", "|")

    # ---------------- Build Main UI ----------------
    def build(self):
        # Title label at top
        ttk.Label(self, text="My Notes Organizer", font=("Segoe UI", 14, "bold")).pack(pady=8)

        # Top bar: category dropdown, search entry, sort dropdown
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=6)

        # Category filter
        ttk.Label(top, text="Category:").pack(side="left", padx=(0, 5))
        self.category_filter = ttk.Combobox(
            top, values=self.categories, textvariable=self.category_var,
            state="readonly", width=16
        )
        self.category_filter.current(0)  # Default = "All"
        self.category_filter.pack(side="left", padx=(0, 10))
        self.category_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters_and_populate())
        ttk.Button(top, text="Add Category", command=self.add_category).pack(side="left", padx=(0, 5))
        ttk.Button(top, text="Delete Category", command=self.delete_category).pack(side="left", padx=(0, 10))

        # Search entry (updates in real-time and also works with Enter key)
        search_entry = ttk.Entry(top, textvariable=self.search_var, width=36)
        search_entry.pack(side="left", padx=(0, 8))
        search_entry.bind("<KeyRelease>", lambda e: self.apply_filters_and_populate())
        search_entry.bind("<Return>", lambda e: self.apply_filters_and_populate())

        # Reset filters button
        ttk.Button(top, text="Reset", command=self._reset_filters).pack(side="left", padx=(0, 8))

        # Sort dropdown
        sort_cb = ttk.Combobox(top, textvariable=self.sort_var, width=22, state="readonly")
        sort_cb['values'] = ["Date (newest)", "Date (oldest)", "Title (A → Z)", "Title (Z → A)"]
        sort_cb.bind("<<ComboboxSelected>>", lambda e: self.apply_filters_and_populate())
        sort_cb.pack(side="right", padx=(8, 0))
        ttk.Label(top, text="Sort:").pack(side="right")

        # -------- Notes list area (Treeview + Scrollbars) --------
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=10, pady=6)

        columns = ("category", "title", "tags", "timestamp")
        self.tree = ttk.Treeview(container, columns=columns, show="headings")

        # Define headings (clickable for sorting)
        for col in columns:
            self.tree.heading(col, text=col.title(), command=lambda c=col: self._heading_sort_toggle(c))

        # Set column widths
        self.tree.column("category", width=120, anchor="w")
        self.tree.column("title", width=260, anchor="w")
        self.tree.column("tags", width=150, anchor="w")
        self.tree.column("timestamp", width=150, anchor="center")

        # Add scrollbars
        vsb = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Place treeview + scrollbars in grid layout
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Double-click event: show note details
        self.tree.bind("<Double-1>", self.show_note_details)

        # -------- Bottom button area --------
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side="bottom", fill="x", pady=6)

        # Add, Delete, Refresh buttons
        add_btn = ttk.Button(btn_frame, text="Add Note", command=self.add_note)
        del_btn = ttk.Button(btn_frame, text="Delete Note", command=self.delete_note)
        ref_btn = ttk.Button(btn_frame, text="Refresh", command=self.load_notes)
        add_btn.grid(row=0, column=0, sticky="ew", padx=6, pady=4)
        del_btn.grid(row=0, column=1, sticky="ew", padx=6, pady=4)
        ref_btn.grid(row=0, column=2, sticky="ew", padx=6, pady=4)

        # Ensure equal button widths
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        btn_frame.grid_columnconfigure(2, weight=1)

    # ---------------- Helper: Reset filters ----------------
    def _reset_filters(self):
        # Reset all filters to default values
        self.category_var.set("All")
        self.search_var.set("")
        self.sort_var.set("Date (newest)")
        self.apply_filters_and_populate()

    # ---------------- Action: Change category ----------------
    def change_category(self, category):
        # Change selected category and refresh notes
        self.category_var.set(category)
        self.apply_filters_and_populate()

    # ---------------- Load notes from file (preserve line breaks) ----------------
    def load_notes(self):
        """Load all notes belonging to current user into self.notes"""
        self.notes.clear()
        if not os.path.exists(NOTES_FILE):
            self.tree.delete(*self.tree.get_children())
            return

        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.rstrip("\n")
                # Use maxsplit=6 so that content can contain separator symbol
                parts = line.split(SPLIT, 6)
                if len(parts) < 7:
                    continue
                user, category, title, tags, content, attachments, ts = parts
                if user != self.username:
                    continue
                # Restore line breaks in content
                content = content.replace("\\n", "\n")
                self.notes.append({
                    "category": self.unescape_field(category),
                    "title": self.unescape_field(title),
                    "tags": self.unescape_field(tags.strip()),
                    "content": self.unescape_field(content).replace("\\n", "\n"),
                    "attachments": attachments,
                    "timestamp": ts,
                    "display_timestamp": ts[:16]
                })

        # Sort notes by timestamp (newest first by default)
        try:
            self.notes.sort(key=lambda n: datetime.strptime(n["timestamp"], "%Y-%m-%d %H:%M:%S"), reverse=True)
        except Exception:
            pass

        self.apply_filters_and_populate()

    # ---------------- Apply filter + sort, then populate treeview ----------------
    def apply_filters_and_populate(self):
        cat = self.category_var.get()
        kw = self.search_var.get().strip().lower()
        mode = self.sort_var.get()

        # Filter notes by category and keyword
        filtered = []
        for n in self.notes:
            if cat != "All" and n["category"] != cat:
                continue
            if kw:
                if kw not in n["title"].lower() and kw not in n["tags"].lower():
                    continue
            filtered.append(n)

        # Apply sorting
        try:
            if mode == "Date (newest)":
                filtered.sort(key=lambda x: datetime.strptime(x["timestamp"], "%Y-%m-%d %H:%M:%S"), reverse=True)
            elif mode == "Date (oldest)":
                filtered.sort(key=lambda x: datetime.strptime(x["timestamp"], "%Y-%m-%d %H:%M:%S"))
            elif mode == "Title (A → Z)":
                filtered.sort(key=lambda x: x["title"].lower())
            elif mode == "Title (Z → A)":
                filtered.sort(key=lambda x: x["title"].lower(), reverse=True)
        except Exception:
            pass

        # Populate treeview and build iid -> note mapping for reliable lookup
        self.tree.delete(*self.tree.get_children())

        # Reset mapping
        self._iid_map.clear()

        for n in filtered:
            # Insert row and capture the item id (iid)
            iid = self.tree.insert("", "end", values=(n["category"], n["title"], n["tags"], n["display_timestamp"]))
            # Map iid to the note object (reference to dict stored in memory)
            self._iid_map[iid] = n

    # ---------------- Toggle heading sorting ----------------
    def _heading_sort_toggle(self, col):
        # Toggle sorting mode when clicking on column headers
        cur = self.sort_var.get()
        if col == "timestamp":
            # Toggle between newest and oldest
            self.sort_var.set("Date (oldest)" if cur == "Date (newest)" else "Date (newest)")
        elif col == "title":
            self.sort_var.set("Title (Z → A)" if cur == "Title (A → Z)" else "Title (A → Z)")
        self.apply_filters_and_populate()

    # ---------------- Show details (double-click) ----------------
    def show_note_details(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]

        # Prefer direct mapping lookup by iid
        note = self._iid_map.get(iid)
        if not note:
            # Fallback: try retrieving values from item and match by title+display_timestamp
            item = self.tree.item(iid)
            title = item["values"][1]
            display_ts = item["values"][3]  # truncated displayed timestamp
            note = next((n for n in self.notes if n["title"] == title and n.get("display_timestamp") == display_ts), None)
            if not note:
                # Final fallback: match by title only (legacy)
                note = next((n for n in self.notes if n["title"] == title), None)
        if not note:
            return

        win = tk.Toplevel(self)
        win.title(f"Note - {note['title']}")
        win.geometry("850x850")
        win.resizable(True, True)
        win.attributes("-topmost", True)

        ttk.Label(win, text=f"Category: {note['category']}", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=(8, 2))
        ttk.Label(win, text=f"Title: {note['title']}", font=("Segoe UI", 12)).pack(anchor="w", padx=10, pady=(0, 4))
        ttk.Label(win, text=f"Tags: {note['tags']}").pack(anchor="w", padx=10, pady=(0, 4))
        ttk.Label(win, text=f"Last Edited: {note['timestamp']}").pack(anchor="w", padx=10, pady=(0, 8))

        content_box = tk.Text(win, wrap="word", height=12)
        content_box.insert("1.0", note["content"])
        content_box.config(state="disabled")
        content_box.pack(fill="both", expand=True, padx=10, pady=6)

        # Attachments with horizontal scroll
        if note["attachments"] and note["attachments"] != "None":
            att_frame = ttk.LabelFrame(win, text="Attachments")
            att_frame.pack(fill="x", padx=10, pady=6)

            canvas = tk.Canvas(att_frame, height=200)
            h_scroll = ttk.Scrollbar(att_frame, orient="horizontal", command=canvas.xview)
            canvas.configure(xscrollcommand=h_scroll.set)

            canvas.pack(side="top", fill="x", expand=True)
            h_scroll.pack(side="bottom", fill="x")

            inner_frame = ttk.Frame(canvas)
            canvas.create_window((0, 0), window=inner_frame, anchor="nw")

            def update_scroll_region(event=None):
                canvas.configure(scrollregion=canvas.bbox("all"))

            inner_frame.bind("<Configure>", update_scroll_region)

            for fn in note["attachments"].split(","):
                path = os.path.join(IMAGE_FOLDER, fn.strip())
                if os.path.exists(path):
                    try:
                        img = Image.open(path)
                        img.thumbnail((220, 160))
                        ph = ImageTk.PhotoImage(img)
                    except Exception:
                        continue
                    lbl = ttk.Label(inner_frame, image=ph)
                    lbl.image = ph
                    lbl.pack(side="left", padx=6, pady=6)
                    lbl.bind("<Double-1>", lambda e, p=path: self.show_full_image(p))

        btnf = ttk.Frame(win)
        btnf.pack(pady=8)
        ttk.Button(btnf, text="Edit", command=lambda: self.edit_note_window(note, win)).pack(side="left", padx=6)
        ttk.Button(btnf, text="Close", command=win.destroy).pack(side="left", padx=6)

    # ---------------- Enlarge image (independent window) ----------------
    def show_full_image(self, path):
        if not os.path.exists(path):
            return
        top = tk.Toplevel(self)
        top.title("Image Viewer")
        # Try to maximize window (but still keep title bar visible)
        try:
            top.state("zoomed")
        except Exception:
            top.geometry(f"{top.winfo_screenwidth()}x{top.winfo_screenheight()}")

        # Resize image to fit screen
        img = Image.open(path)
        screen_w = top.winfo_screenwidth()
        screen_h = top.winfo_screenheight()
        img.thumbnail((screen_w - 120, screen_h - 120))
        ph = ImageTk.PhotoImage(img)
        lbl = ttk.Label(top, image=ph)
        lbl.image = ph
        lbl.pack(expand=True)

        # Close button + Esc key
        close_btn = ttk.Button(top, text="Close (Esc)", command=top.destroy)
        close_btn.place(relx=0.98, rely=0.02, anchor="ne")
        top.bind("<Escape>", lambda e: top.destroy())
        top.attributes("-topmost", True)

    # ---------------- Add / Edit shared window ----------------
    def add_note(self):
        # Open the add note window (editing=False)
        self._note_window(editing=False, note=None)

    def edit_note_window(self, note, parent_win):
        # Close details window and open edit window
        try:
            parent_win.destroy()
        except Exception:
            pass
        self._note_window(editing=True, note=note)

    def _note_window(self, editing=False, note=None):
        """
        Shared window for adding or editing a note.
        - Uses grid layout, resizes with window
        - Uploaded images are shown as thumbnails with "Remove" buttons
        - Double-click thumbnail to enlarge
        """
        win = tk.Toplevel(self)
        win.title("Edit Note" if editing else "Add Note")
        win.geometry("1000x750")
        win.resizable(True, True)
        win.attributes("-topmost", True)

        # Current attachments (filenames only, stored in notes_images folder)
        attachments = []
        if editing and note and note.get("attachments") and note["attachments"] != "None":
            attachments = [p.strip() for p in note["attachments"].split(",") if p.strip()]

        # Main container
        main = ttk.Frame(win, padding=10)
        main.grid(sticky="nsew")
        win.grid_rowconfigure(0, weight=1)
        win.grid_columnconfigure(0, weight=1)

        # Left side: form fields
        form = ttk.Frame(main)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        form.grid_columnconfigure(1, weight=1)
        form.grid_rowconfigure(4, weight=1)

        # Category dropdown
        ttk.Label(form, text="Category:").grid(row=0, column=0, sticky="w", pady=6)
        category_var = tk.StringVar(value=(note["category"] if editing else "General"))
        category_combo = ttk.Combobox(form, textvariable=category_var, values=self.categories[1:], state="readonly")
        category_combo.grid(row=0, column=1, sticky="ew", pady=6)

        # Title entry
        ttk.Label(form, text="Title:").grid(row=1, column=0, sticky="w", pady=6)
        title_var = tk.StringVar(value=(note["title"] if editing else ""))
        ttk.Entry(form, textvariable=title_var).grid(row=1, column=1, sticky="ew", pady=6)

        # Tags entry
        ttk.Label(form, text="Tags:").grid(row=2, column=0, sticky="w", pady=6)
        tags_var = tk.StringVar(value=(note["tags"] if editing else ""))
        ttk.Entry(form, textvariable=tags_var).grid(row=2, column=1, sticky="ew", pady=6)

        # Content text box
        ttk.Label(form, text="Content:").grid(row=3, column=0, sticky="nw", pady=6)
        content_text = tk.Text(form, wrap="word")
        if editing:
            content_text.insert("1.0", note["content"])
        content_text.grid(row=3, column=1, sticky="nsew", pady=6)

        # ---------- Right side: Thumbnail preview area ----------
        preview = ttk.LabelFrame(main, text="Attachments (Double-click to enlarge)")
        preview.grid(row=0, column=1, sticky="nsew")
        preview.grid_rowconfigure(0, weight=1)
        preview.grid_columnconfigure(0, weight=1)

        thumb_canvas = tk.Canvas(preview, highlightthickness=0)
        thumb_canvas.grid(row=0, column=0, sticky="nsew")
        thumb_vsb = ttk.Scrollbar(preview, orient="vertical", command=thumb_canvas.yview)
        thumb_vsb.grid(row=0, column=1, sticky="ns")
        thumb_canvas.configure(yscrollcommand=thumb_vsb.set)

        thumb_frame = ttk.Frame(thumb_canvas)
        thumb_window = thumb_canvas.create_window((0, 0), window=thumb_frame, anchor="nw")

        # Store thumbnail references to avoid garbage collection
        self._thumb_refs = []
        self._thumb_items = []

        def _on_thumb_frame_configure(event):
            thumb_canvas.configure(scrollregion=thumb_canvas.bbox("all"))
        thumb_frame.bind("<Configure>", _on_thumb_frame_configure)

        # Arrange thumbnails in grid-like flow
        def arrange_thumbs():
            thumb_frame.update_idletasks()
            canvas_w = thumb_canvas.winfo_width()
            if canvas_w <= 1:
                thumb_frame.after(80, arrange_thumbs)
                return
            cell_w = 180
            cols = max(1, canvas_w // cell_w)
            for idx, box in enumerate(self._thumb_items):
                r = idx // cols
                c = idx % cols
                box.grid_configure(row=r, column=c, padx=6, pady=6, sticky="nw")
            thumb_frame.update_idletasks()
            thumb_canvas.configure(scrollregion=thumb_canvas.bbox("all"))

        thumb_canvas.bind("<Configure>", lambda e: arrange_thumbs())

        # Create a single thumbnail box for one image file
        def create_thumb(filename):
            path = os.path.join(IMAGE_FOLDER, filename)
            if not os.path.exists(path):
                return
            try:
                img = Image.open(path)
                img.thumbnail((160, 120))
                ph = ImageTk.PhotoImage(img)
            except Exception:
                return

            box = ttk.Frame(thumb_frame)
            lbl = ttk.Label(box, image=ph)
            lbl.image = ph
            lbl.pack()
            lbl.bind("<Double-1>", lambda e, p=path: self.show_full_image(p))

            # Button to remove attachment from list
            def _remove():
                try:
                    if filename in attachments:
                        attachments.remove(filename)
                except Exception:
                    pass
                try:
                    self._thumb_items.remove(box)
                except ValueError:
                    pass
                box.destroy()
                arrange_thumbs()

            del_btn = ttk.Button(box, text="Remove", command=_remove)
            del_btn.pack(pady=4)

            self._thumb_refs.append(ph)
            self._thumb_items.append(box)
            arrange_thumbs()

        # Show thumbnails for existing attachments
        for fn in attachments[:]:
            create_thumb(fn)

        # Upload image button
        def upload_image():
            win.attributes("-topmost", False)  # prevent file dialog from being hidden
            file_path = filedialog.askopenfilename(parent=win, filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
            win.attributes("-topmost", True)
            if not file_path:
                return
            filename = os.path.basename(file_path)
            dest = os.path.join(IMAGE_FOLDER, filename)
            base, ext = os.path.splitext(filename)
            idx = 1
            # Prevent overwriting files with same name
            while os.path.exists(dest):
                filename = f"{base}_{idx}{ext}"
                dest = os.path.join(IMAGE_FOLDER, filename)
                idx += 1
            try:
                shutil.copy(file_path, dest)
                attachments.append(filename)
                create_thumb(filename)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy image: {e}", parent=win)

        upl_btn = ttk.Button(main, text="Upload Image", command=upload_image)
        upl_btn.grid(row=1, column=0, columnspan=2, sticky="w", padx=6, pady=(8, 10))

        # ---------------- Save / Cancel ----------------
        def do_save():
            category = category_var.get().strip() or "General"
            title = self.escape_field(title_var.get().strip())
            tags = self.escape_field(tags_var.get().strip())
            content = content_text.get("1.0", tk.END).rstrip()
            content_to_store = self.escape_field(content.replace("\n", "\\n"))  # preserve line breaks
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            attach_str = ",".join(attachments) if attachments else "None"

            if not title or not content:
                messagebox.showwarning("Validation", "Title and content cannot be empty.", parent=win)
                return

            if editing and note:
                # Replace existing note by matching username + old title + old timestamp
                new_lines = []
                if os.path.exists(NOTES_FILE):
                    with open(NOTES_FILE, "r", encoding="utf-8") as f:
                        lines = [l.rstrip("\n") for l in f if l.strip()]
                    replaced = False
                    for l in lines:
                        parts = l.split(SPLIT, 6)
                        if len(parts) < 7:
                            new_lines.append(l)
                            continue
                        u, cat, t, tg, cont, att, ts = parts
                        if u == self.username and t == note["title"] and ts == note["timestamp"] and not replaced:
                            # Replace with updated info
                            new_lines.append(f"{self.username}{SPLIT}{category}{SPLIT}{title}{SPLIT}{tags}{SPLIT}{content_to_store}{SPLIT}{attach_str}{SPLIT}{timestamp}")
                            replaced = True
                        else:
                            new_lines.append(l)
                else:
                    new_lines = [f"{self.username}{SPLIT}{category}{SPLIT}{title}{SPLIT}{tags}{SPLIT}{content_to_store}{SPLIT}{attach_str}{SPLIT}{timestamp}"]
                with open(NOTES_FILE, "w", encoding="utf-8") as f:
                    for l in new_lines:
                        f.write(l + "\n")
            else:
                # Append new note to file
                with open(NOTES_FILE, "a", encoding="utf-8") as f:
                    f.write(f"{self.username}{SPLIT}{category}{SPLIT}{title}{SPLIT}{tags}{SPLIT}{content_to_store}{SPLIT}{attach_str}{SPLIT}{timestamp}\n")

            messagebox.showinfo("Saved", "Note saved.", parent=win)
            win.destroy()
            self.load_notes()

        btns = ttk.Frame(main)
        btns.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 4))
        save_btn = ttk.Button(btns, text="Save", command=do_save)
        cancel_btn = ttk.Button(btns, text="Cancel", command=win.destroy)
        save_btn.pack(side="right", padx=6)
        cancel_btn.pack(side="right", padx=6)

        # Allow resizing
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)

    # ---------------- Delete note ----------------
    def delete_note(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Delete", "Please select a note to delete.")
            return
        iid = sel[0]

        # Try to get note directly from mapping
        note_to_delete = self._iid_map.get(iid)

        full_ts = None
        title = None
        if note_to_delete:
            full_ts = note_to_delete.get("timestamp")
            title = note_to_delete.get("title")
        else:
            # Fallback: extract values from tree item and try to match in memory
            item = self.tree.item(iid)
            title = item["values"][1]
            display_ts = item["values"][3]   # displayed timestamp (YYYY-MM-DD HH:MM)
            # Try to find corresponding note in memory by title + display timestamp
            note_to_delete = next((n for n in self.notes if n["title"] == title and n.get("display_timestamp") == display_ts), None)
            if note_to_delete:
                full_ts = note_to_delete.get("timestamp")

        # If still not found, ask user whether to delete all notes with that title (legacy fallback)
        if not note_to_delete:
            confirm = messagebox.askyesno("Confirm", "Exact match not found by displayed timestamp. Delete all notes with this title for your account?", parent=self)
            if not confirm:
                return

        new_lines = []
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                for raw in f:
                    parts = raw.rstrip("\n").split(SPLIT, 6)
                    if len(parts) < 7:
                        continue
                    u, cat, t, tg, cont, att, ts = parts
                    if full_ts is not None:
                        # Remove only the exact record matching username + title + full_ts
                        if not (u == self.username and t == title and ts == full_ts):
                            new_lines.append(raw.rstrip("\n"))
                    else:
                        # Fallback: remove all notes matching username + title
                        if not (u == self.username and t == title):
                            new_lines.append(raw.rstrip("\n"))

        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            for l in new_lines:
                f.write(l + "\n")

        messagebox.showinfo("Deleted", "Note deleted.")
        self.load_notes()

    # ---------------- Category management (Add / Delete) ----------------
    def add_category(self):
        # Small window to add a new category
        win = tk.Toplevel(self)
        win.title("Add Category")
        win.geometry("320x140")
        win.resizable(False, False)
        ttk.Label(win, text="Category name:").pack(pady=(12, 6))
        var = tk.StringVar()
        ttk.Entry(win, textvariable=var).pack(pady=6)

        def do_add():
            name = var.get().strip()
            if not name:
                messagebox.showwarning("Invalid", "Please enter a name.", parent=win)
                return
            if name in self.categories:
                messagebox.showwarning("Invalid", "Category already exists.", parent=win)
                return
            self.categories.append(name)

            if hasattr(self, "category_filter"):
                self.category_filter["values"] = self.categories

            messagebox.showinfo("Added", f"Category '{name}' added.", parent=win)
            self.save_user_categories()
            win.destroy()
            self.apply_filters_and_populate()

        btnf = ttk.Frame(win)
        btnf.pack(pady=8)
        ttk.Button(btnf, text="OK", command=do_add).pack(side="left", padx=6)
        ttk.Button(btnf, text="Cancel", command=win.destroy).pack(side="left", padx=6)

    def delete_category(self):
        # Small window to delete a category
        win = tk.Toplevel(self)
        win.title("Delete Category")
        win.geometry("360x160")
        win.resizable(False, False)
        ttk.Label(win, text="Select category to delete:").pack(pady=(10, 6))
        allowed = [c for c in self.categories if c not in ("All", "General")]
        if not allowed:
            ttk.Label(win, text="No deletable categories.").pack(pady=6)
            ttk.Button(win, text="Close", command=win.destroy).pack(pady=8)
            return
        var = tk.StringVar(value=allowed[0])
        combo = ttk.Combobox(win, values=allowed, textvariable=var, state="readonly")
        combo.pack(pady=6)

        def do_del():
            name = var.get().strip()
            if not name:
                messagebox.showwarning("Invalid", "Please select.", parent=win)
                return
            confirm = messagebox.askyesno("Confirm", f"Delete '{name}'? Notes in it will be moved to General.", parent=win)
            if not confirm:
                return

            # Update file: move notes under this category to General
            new_lines = []
            if os.path.exists(NOTES_FILE):
                with open(NOTES_FILE, "r", encoding="utf-8") as f:
                    for raw in f:
                        parts = raw.rstrip("\n").split(SPLIT, 6)
                        if len(parts) < 7:
                            continue
                        u, cat, t, tg, cont, att, ts = parts
                        if u == self.username and cat == name:
                            new_lines.append(f"{u}{SPLIT}General{SPLIT}{t}{SPLIT}{tg}{SPLIT}{cont}{SPLIT}{att}{SPLIT}{ts}")
                        else:
                            new_lines.append(raw.rstrip("\n"))
            with open(NOTES_FILE, "w", encoding="utf-8") as f:
                for l in new_lines:
                    f.write(l + "\n")

            if name in self.categories:
                self.categories.remove(name)

            if hasattr(self, "category_filter"):
                self.category_filter["values"] = self.categories

            messagebox.showinfo("Deleted", f"Category '{name}' deleted. Notes moved to General.", parent=win)
            self.save_user_categories()
            win.destroy()
            self.load_notes()

        btnf = ttk.Frame(win)
        btnf.pack(pady=10)
        ttk.Button(btnf, text="Delete", command=do_del).pack(side="left", padx=6)
        ttk.Button(btnf, text="Cancel", command=win.destroy).pack(side="left", padx=6)

    # ---------------- Category persistence ----------------
    def load_user_categories(self):
        """
        Load this user's categories from categories.txt file.
        Each line format: username|cat1,cat2,cat3,...
        - If file exists and user is found, return their categories.
        - Ensure "All" is always at the beginning.
        - Ensure "General" is always present as a fallback category.
        - If no record found, return default categories.
        """
        filename = "categories.txt"
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split("|", 1)
                    if len(parts) == 2 and parts[0] == self.username:
                        cats = [c.strip() for c in parts[1].split(",") if c.strip()]
                        if "All" not in cats:
                            cats.insert(0, "All")
                        if "General" not in cats:
                            cats.append("General")
                        return cats
        return ["All", "School", "Personal", "Work", "General"]

    def save_user_categories(self):
        """
        Save this user's categories into categories.txt file.
        - If user already exists in file, replace their line.
        - If not, append a new line for this user.
        - Format: username|cat1,cat2,cat3,...
        """
        filename = "categories.txt"
        lines = []
        found = False
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split("|", 1)
                    if len(parts) == 2 and parts[0] == self.username:
                        lines.append(f"{self.username}|{','.join(self.categories)}\n")
                        found = True
                    else:
                        lines.append(line)
        if not found:
            lines.append(f"{self.username}|{','.join(self.categories)}\n")

        with open(filename, "w", encoding="utf-8") as f:
            f.writelines(lines)

# End of notes.py