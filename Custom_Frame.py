from ttkbootstrap import Frame, Label
from Player import Player
from dictionnaries import teams_color_dictionary, packetDictionnary, tyres_dictionnary, tyres_color_dictionnary, grey
from Session import Session


class Custom_Frame(Frame): # Frame Tableau
    def __init__(self, parent, name, id, n_lines):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.name = name
        self.id = id
        self.n_lines = n_lines
        self.liste_frame = []
        for i in range(n_lines):
            frame = Frame(self)
            frame.grid(row=i, column=0, sticky="nsew", pady=2, padx=5)
            label = Label(frame, text="Driver"+str(i), font="Helvetica 12")
            label.pack(side='left')
            self.liste_frame.append((frame, label, i))
        self.pack(expand=True, fill="both")


class Players_Frame(Custom_Frame):
    def __init__(self, parent, name, id):
        super().__init__(parent, name, id, 20)
        self.label_tyres = []
        for i in range(self.n_lines):
            label = Label(self.liste_frame[i][0], text="S", foreground="#FF0000", font="Helvetica 12")
            label.pack(side='left')
            self.liste_frame[i][1].pack_forget()
            self.liste_frame[i][1].pack(side='left')
            self.label_tyres.append((label, i))

    def sort(self, LISTE_JOUEURS:list[Player], session):
        self.liste_frame.sort(key=lambda e : LISTE_JOUEURS[e[2]].position)
        self.label_tyres.sort(key=lambda e : LISTE_JOUEURS[e[1]].position)
        for i in range(self.n_lines):
            frame, label, j = self.liste_frame[i]
            joueur = LISTE_JOUEURS[j]
            frame.grid(row=i, column=0)
            if joueur.position != 100:
                label.config(text=joueur.printing(self.id, LISTE_JOUEURS, session.Seance), foreground=teams_color_dictionary[joueur.teamId] if not joueur.hasRetired else grey)
                self.label_tyres[i][0].config(text=tyres_dictionnary[joueur.tyres], foreground=tyres_color_dictionnary[joueur.tyres])
            else:
                label.config(text="")
                self.label_tyres[i][0].config(text="")

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
        for i in range(session.nb_weatherForecastSamples):
            frame, label, j = self.liste_frame[i]
            label.config(text=session.weatherList[i])
        for i in range(session.nb_weatherForecastSamples, 20):
            frame, label, j = self.liste_frame[i]
            label.config(text="")
        

