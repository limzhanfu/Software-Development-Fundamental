import tkinter as tk
from tkinter import ttk

class CalendarSwitcher:
    def __init__(self, frame):
        self.frame = frame
        self.list = []  

    def add_button(self ,text ,command  ):
        self.list.append(ttk.Button(master=self.frame ,text=text ,command=command))

    def render_btn(self):
        for i in self.list:
            i.pack(side=tk.LEFT, padx=4)


