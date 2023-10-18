from ttkbootstrap import Window, Notebook, Frame, Canvas, Menu
from tkinter import Label

screen = Window(themename="darkly")

import math
from packet_management import *
import json
import time
from Player import Player
from Session import Session
from dictionnaries import *
from parser2023 import Listener
from Custom_Frame import Custom_Frame


def init_20_players():
    for _ in range(22):
        LISTE_JOUEURS.append(Player())


def update_motion(packet):  # Packet 0
    if not created_map:
        create_map()
    for i in range(22):
        if LISTE_JOUEURS[i].worldPositionX != 0:
            LISTE_JOUEURS[i].Xmove = packet.m_car_motion_data[i].m_world_position_x - LISTE_JOUEURS[i].worldPositionX
            LISTE_JOUEURS[i].Zmove = packet.m_car_motion_data[i].m_world_position_z - LISTE_JOUEURS[i].worldPositionZ
        LISTE_JOUEURS[i].worldPositionX = packet.m_car_motion_data[i].m_world_position_x
        LISTE_JOUEURS[i].worldPositionZ = packet.m_car_motion_data[i].m_world_position_z
    update_map()


def update_session(packet):  # Packet 1
    global created_map
    session.trackTemperature = packet.m_weather_forecast_samples[0].m_track_temperature
    session.airTemperature = packet.m_weather_forecast_samples[0].m_air_temperature
    session.nbLaps = packet.m_total_laps
    session.Seance = packet.m_session_type
    session.time_left = packet.m_session_time_left
    if session.track != packet.m_track_id: # Track has changed
        session.track = packet.m_track_id
        created_map=False
    session.marshalZones = packet.m_marshal_zones  # Array[21]
    session.marshalZones[0].m_zone_start = session.marshalZones[0].m_zone_start - 1
    session.num_marshal_zones = packet.m_num_marshal_zones
    session.safetyCarStatus = packet.m_safety_car_status
    session.trackLength = packet.m_track_length
    if session.currentLap > session.nbLaps:
        session.Finished = True
    session.clear_slot()
    for i in range(packet.m_num_weather_forecast_samples):
        slot = packet.m_weather_forecast_samples[i]
        session.add_slot(slot)
    draw_title()


def create_map():
    global created_map
    if session.trackLength==0:
        return
    cmi = 1
    L0 = []
    L = []
    name, d, x_const, z_const = track_dictionary[session.track]
    with open(f"tracks/{name}_2020_racingline.txt", "r") as file:
        for index, line in enumerate(file):
            created_map = True
            if index not in [0, 1]:
                dist, z, x, y, _, _ = line.strip().split(",")
                if cmi == 1:
                    L0.append((float(z) / d + x_const, float(x) / d + z_const))
                else:
                    L.append((float(z) / d + x_const, float(x) / d + z_const))
                if float(dist) / session.trackLength > session.marshalZones[cmi].m_zone_start and not (cmi==1 and len(session.segments)>3):
                    cmi = (cmi + 1) % session.num_marshal_zones
                    session.segments.append(map_canvas.create_line(L, width=3))
                    L = []
                L.append((float(z) / d + x_const, float(x) / d + z_const))
    session.segments.insert(0, map_canvas.create_line(L0, width=3))
    for joueur in LISTE_JOUEURS:
        joueur.oval = map_canvas.create_oval(joueur.worldPositionX / d + x_const - WIDTH_POINTS,
                                             joueur.worldPositionZ / d + z_const - WIDTH_POINTS,
                                             joueur.worldPositionX / d + x_const + WIDTH_POINTS,
                                             joueur.worldPositionZ / d + z_const + WIDTH_POINTS, outline="")
        joueur.etiquette = map_canvas.create_text(joueur.worldPositionX / d + x_const + 25,
                                                  joueur.worldPositionZ / d + z_const - 25,
                                                  text=joueur.name, font=("Cousine", 13))


def update_map():
    _, d, x, z = track_dictionary[session.track]
    for joueur in LISTE_JOUEURS:
        if joueur.etiquette == "":
            joueur.etiquette = map_canvas.create_text(joueur.worldPositionX / d + x, joueur.worldPositionZ / d + z,
                                                      text=joueur.name)
        if joueur.position != 0:
            map_canvas.move(joueur.oval, joueur.Xmove / d, joueur.Zmove / d)
            map_canvas.itemconfig(joueur.oval, fill=teams_color_dictionary[joueur.teamId])
            map_canvas.move(joueur.etiquette, joueur.Xmove / d, joueur.Zmove / d)
            map_canvas.itemconfig(joueur.etiquette, fill=teams_color_dictionary[joueur.teamId], text=joueur.name)


def draw_title():
    top_label1.config(text=session.title_display())
    top_label2.config(text=safetyCarStatusDict[session.safetyCarStatus])
    match session.safetyCarStatus:
        case 4:
            top_label2.config(bg="red")
        case 0:
            top_label2.config(bg=screen.cget("background"))
        case _:
            top_label2.config(bg="yellow")


def init_window():
    global map_canvas
    screen.columnconfigure(0, weight=1)
    screen.rowconfigure(0, pad=75)
    screen.rowconfigure(1, weight=1)

    screen.title("Telemetry Application")

    top_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
    main_frame.grid(row=1, column=0, sticky="nsew")

    notebook = Notebook(main_frame)
    notebook.pack(expand=True, fill="both")

    LISTE_FRAMES.append(Custom_Frame(notebook, "Main Menu", 1))
    LISTE_FRAMES.append(Custom_Frame(notebook, "Damage", 2))
    LISTE_FRAMES.append(Custom_Frame(notebook, "Temperatures", 3))
    LISTE_FRAMES.append(Custom_Frame(notebook, "Laps", 4))
    LISTE_FRAMES.append(Custom_Frame(notebook, "ERS & Fuel", 5))
    map = Frame(notebook)
    LISTE_FRAMES.append(map)
    map.pack(expand=True, fill="both")
    map_canvas = Canvas(map)
    map_canvas.pack(expand=True, fill='both')

    weather = Frame(notebook)
    LISTE_FRAMES.append(weather)
    weather.pack(expand=True, fill="both")

    packet = Frame(notebook)
    LISTE_FRAMES.append(packet)
    packet.pack(expand=True, fill="both")
    for i in range(5):
        notebook.add(LISTE_FRAMES[i], text=LISTE_FRAMES[i].name)
    notebook.add(LISTE_FRAMES[5], text="Map")
    notebook.add(LISTE_FRAMES[6], text="Weather Forecast")
    notebook.add(LISTE_FRAMES[7], text="Packet Reception")

    top_label1.place(relx=0.0, rely=0.5, anchor='w')
    top_label2.place(relx=1, rely=0.5, anchor='e')
    top_frame.columnconfigure(0, weight=3)

    screen.geometry("1080x700")
    screen.protocol("WM_DELETE_WINDOW", close_window)

    menubar = Menu(screen)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="PORT Selection", command=lambda : port_selection(dictionnary_settings, listener, PORT))
    filemenu.add_command(label="UDP Redirect", command=lambda : UDP_Redirect(dictionnary_settings, listener, PORT))
    menubar.add_cascade(label="Settings", menu=filemenu)
    screen.config(menu=menubar)


def close_window():
    global running
    running = False
'''
indice 7,27,28,29
21 = multiple warnings
'''
created_map = False
WIDTH_POINTS = 6
function_hashmap = {
    0: update_motion,
    1: update_session,
    2: update_lap_data,
    3: warnings,
    4: update_participants,
    5: update_car_setups,
    6: update_car_telemetry,
    7: update_car_status,
    8: nothing,
    9: nothing,
    10: update_car_damage,
    11: nothing,
    12: nothing,
    13: nothing

}

packet_received = [0]*14
last_update = time.time()
LISTE_FRAMES = []
liste_button: list = ["Main Menu", "Damage", "Temperatures", "Laps", "Map", "ERS & Fuel", "Weather Forecast",
                              "Packet Reception"]
with open("settings.txt", "r") as f:
    dictionnary_settings = json.load(f)

top_frame = Frame(screen)
main_frame = Frame(screen)

top_label1 = Label(top_frame, text="Course ", bg="purple", font=("Arial", 24), padx=10)
top_label2 = Label(top_frame, text="", bg="yellow", font=("Arial", 24), pady=100, padx=30, width=10)

init_window()
init_20_players()

running = True
PORT = [int(dictionnary_settings["port"])]
listener = [Listener(port=PORT[0],
                    redirect=dictionnary_settings["redirect_active"],
                    adress=dictionnary_settings["ip_adress"],
                    redirect_port=int(dictionnary_settings["redirect_port"]))]


while running:
    a = listener[0].get()
    if a is not None:
        header, packet = a
        packet_received[header.m_packet_id]+=1
        function_hashmap[header.m_packet_id](packet)
        update_frame(LISTE_FRAMES, LISTE_JOUEURS, session)
    if time.time() > last_update+1:
        last_update = time.time()
        session.packet_received = packet_received[:]
        packet_received = [0]*14
    screen.update()
    screen.update_idletasks()
    

listener[0].socket.close()
quit()
