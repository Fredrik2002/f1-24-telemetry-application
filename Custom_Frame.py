from ttkbootstrap import Frame
from tkinter import Label
from Player import Player
from dictionnaries import teams_color_dictionary


class Custom_Frame(Frame): # Frame Tableau
    def __init__(self, parent, name, id):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.name = name
        self.id = id
        self.liste_frame = []
        self.liste_label = []
        for i in range(20):
            frame = Frame(self)
            frame.grid(row=i, column=0, sticky="nsew", pady=2, padx=5)
            label = Label(frame, text="Hello"+str(i), font="Helvetica 12")
            label.pack(side='left')
            self.liste_frame.append((frame, label, i))
        self.pack(expand=True, fill="both")

    def sort(self, LISTE_JOUEURS:list[Player], session):
        self.liste_frame.sort(key=lambda e : LISTE_JOUEURS[e[2]].position)
        for i in range(20):
            frame, label, j = self.liste_frame[i]
            frame.grid(row=i, column=0)
            if LISTE_JOUEURS[j].position != 100:
                label.config(text=LISTE_JOUEURS[j].printing(self.id, LISTE_JOUEURS, session.Seance), fg=teams_color_dictionary[LISTE_JOUEURS[j].teamId])
            else:
                label.config(text="")
