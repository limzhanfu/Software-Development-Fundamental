from tkinter import ttk
import tkinter as tk

class View:
    def __init__(self ,master):
        self._top_frame = ttk.Frame(master)
        self._month_label = ttk.Label(self._top_frame, text="", font=("Segoe UI", 14, "bold"))
        self._main_frame = ttk.Frame(master)
        
        self._top_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=6)
        self._month_label.pack(side=tk.LEFT, padx=12)
        self._main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)  

    def clear_main(self):
        for w in self._main_frame.winfo_children():
            w.destroy()  

    def get_top_frame(self):
        return self._top_frame
    
    def get_main_frame(self):
        return self._main_frame
    
    def get_month_label(self):
        return self._month_label
    
    main_frame = property(get_main_frame)
    top_frame = property(get_top_frame)
    month_label = property(get_month_label)