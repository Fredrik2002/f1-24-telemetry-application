from ttkbootstrap import Frame
from tkinter import Label
from Player import Player
from dictionnaries import teams_color_dictionary, packetDictionnary
from Session import Session


class Custom_Frame(Frame): # Frame Tableau
    def __init__(self, parent, name, id, n_lines):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.name = name
        self.id = id
        self.n_lines = n_lines
        self.liste_frame = []
        self.liste_label = []
        for i in range(n_lines):
            frame = Frame(self)
            frame.grid(row=i, column=0, sticky="nsew", pady=2, padx=5)
            label = Label(frame, text="Hello"+str(i), font="Helvetica 12")
            label.pack(side='left')
            self.liste_frame.append((frame, label, i))
        self.pack(expand=True, fill="both")


class Players_Frame(Custom_Frame):
    def __init__(self, parent, name, id):
        super().__init__(parent, name, id, 20)

    def sort(self, LISTE_JOUEURS:list[Player], session):
        self.liste_frame.sort(key=lambda e : LISTE_JOUEURS[e[2]].position)
        for i in range(self.n_lines):
            frame, label, j = self.liste_frame[i]
            frame.grid(row=i, column=0)
            if LISTE_JOUEURS[j].position != 100:
                label.config(text=LISTE_JOUEURS[j].printing(self.id, LISTE_JOUEURS, session.Seance), fg=teams_color_dictionary[LISTE_JOUEURS[j].teamId])
            else:
                label.config(text="")

class Packet_Reception_Frame(Custom_Frame):
    def __init__(self, parent, name, id):
        super().__init__(parent, name, id, 14)

    def sort(self, packet_received):
        for i in range(14):
            frame, label, j = self.liste_frame[i]
            label.config(text=f"{packetDictionnary[i]} : {packet_received[i]}/s")


class Weather_Forecast_Frame(Custom_Frame):
    def __init__(self, parent, name, id, n_lines):
        super().__init__(parent, name, id, n_lines)

    def sort(self, session : Session):
        if session.nb_weatherForecastSamples!=self.n_lines:
            super().__init__(self.parent, self.name, self.id, session.nb_weatherForecastSamples)
        for i in range(self.n_lines):
            frame, label, j = self.liste_frame[i]
            label.config(text=session.weatherList[i])
        

