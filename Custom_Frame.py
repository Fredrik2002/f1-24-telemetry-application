from tkinter import *
from Player import Player


class Custom_Frame(Frame): # Frame Tableau
    def __init__(self, parent, name):
        super().__init__(parent, background="red")
        self.columnconfigure(0, weight=1)
        self.name = name
        self.liste_frame = []
        for i in range(20):
            frame = Frame(self, background="blue")
            frame.grid(row=i, column=0, sticky="nsew", pady=2, padx=5)
            label = Label(frame, text="Hello"+str(i))
            label.pack(side='left')
            self.liste_frame.append((frame, i))
        self.pack(expand=True, fill="both")

    def sort(self, LISTE_JOUEURS:list[Player]):
        self.liste_frame.sort(key=lambda e : LISTE_JOUEURS[e[1]].position)
        for i in range(len(LISTE_JOUEURS)):
            self.liste_frame[i][0].grid(row=i, column=0)