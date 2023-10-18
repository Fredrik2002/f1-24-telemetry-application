import math
from tkinter import *
from tkinter import ttk

screen = Tk()
import json
import time
from Player import Player
from Session import Session
from dictionnaries import *
from parser2023 import Listener
from Custom_Frame import Custom_Frame

standings = [214, 215, 224, 99, 117, 90, 178, 129, 214, 205]
updated_standings = standings[:]
F2_teams = ["MnT", "RVL", "ASAC", "VRA", "RR", "WSC", "CBR", "GRR", "SRT", "QSL"]
bareme_points = [0, 30, 26, 23, 20, 18, 16, 14, 12, 10, 8, 6, 5, 4, 3, 2, 1, 1, 1, 1, 1]


def init_20_players():
    for _ in range(22):
        LISTE_JOUEURS.append(Player())


def update_motion(packet):  # Packet 0
    for i in range(22):
        if LISTE_JOUEURS[i].worldPositionX != 0:
            LISTE_JOUEURS[i].Xmove = packet.m_car_motion_data[i].m_world_position_x - LISTE_JOUEURS[i].worldPositionX
            LISTE_JOUEURS[i].Zmove = packet.m_car_motion_data[i].m_world_position_z - LISTE_JOUEURS[i].worldPositionZ
        LISTE_JOUEURS[i].worldPositionX = packet.m_car_motion_data[i].m_world_position_x
        LISTE_JOUEURS[i].worldPositionZ = packet.m_car_motion_data[i].m_world_position_z
        if LISTE_JOUEURS[i].position != 0:
            # print(LISTE_JOUEURS[i].worldPositionX, LISTE_JOUEURS[i].worldPositionZ, LISTE_JOUEURS[i].position)
            pass
    # print()
    if clicked_button == 4:
        update_map()


def update_session(packet):  # Packet 1
    global session
    session.trackTemperature = packet.m_weather_forecast_samples[0].m_track_temperature
    session.airTemperature = packet.m_weather_forecast_samples[0].m_air_temperature
    session.nbLaps = packet.m_total_laps
    session.Seance = packet.m_session_type
    session.time_left = packet.m_session_time_left
    if session.track != packet.m_track_id:
        session.track = packet.m_track_id
        if clicked_button == 4:
            for element in main_frame.winfo_children():
                element.destroy()
            build_canvas()
            create_map()
    session.marshalZones = packet.m_marshal_zones  # Array[21]
    if clicked_button == 4:
        session.update_marshal_zones(map_canvas)
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


def update_lap_data(packet):  # Packet 2
    global tour_precedent, updated_standings
    updated_standings = standings[:]
    mega_array = packet.m_lap_data
    for index in range(22):
        element = mega_array[index]
        joueur = LISTE_JOUEURS[index]
        joueur.position = element.m_car_position

        if joueur.teamId != -1 and joueur.teamId < 10 and joueur.aiControlled == 0:
            updated_standings[joueur.teamId] += bareme_points[joueur.position]
        joueur.lastLapTime = round(element.m_last_lap_time_in_ms, 3)
        joueur.pit = element.m_pit_status
        joueur.driverStatus = element.m_driver_status
        joueur.penalties = element.m_penalties
        joueur.currentLapTime = element.m_current_lap_time_in_ms

        if element.m_sector1_time_in_ms == 0 and joueur.currentSectors[
            0] != 0:  # On attaque un nouveau tour
            joueur.lastLapSectors = joueur.currentSectors[:]
            joueur.lastLapSectors[2] = float(
                '%.3f' % (joueur.lastLapTime / 1_000 - joueur.lastLapSectors[0] - joueur.lastLapSectors[1]))

        joueur.currentSectors = [float('%.3f' % (element.m_sector1_time_in_ms / 1000)),
                                 float('%.3f' % (element.m_sector2_time_in_ms / 1000)), 0]
        if joueur.bestLapTime > element.m_last_lap_time_in_ms != 0 or LISTE_JOUEURS[
            index].bestLapTime == 0:
            joueur.bestLapTime = element.m_last_lap_time_in_ms
            joueur.bestLapSectors = joueur.lastLapSectors[:]
        if joueur.bestLapTime < session.bestLapTime and element.m_last_lap_time_in_ms != 0 or \
                joueur.bestLapTime == 0:
            session.bestLapTime = joueur.bestLapTime
            session.idxBestLapTime = index
        if element.m_car_position == 1:
            session.currentLap = mega_array[index].m_current_lap_num
            session.tour_precedent = session.currentLap - 1
        try:
            joueur.lapDistance = math.floor(
                element.m_lap_distance / session.trackLength * len(joueur.minisectors)) % len(joueur.minisectors)
            # Si element.lapDistance = trackLength, joueur.lapDistance = 100
            if index == MnT_player_index:
                # print(joueur.lapDistance)
                pass
        except ZeroDivisionError:
            return

        if joueur.current_mini_sect != joueur.lapDistance:
            joueur.minisectors[joueur.lapDistance] = time.time()
            joueur.current_mini_sect = joueur.lapDistance


def warnings(packet):  # Packet 3
    if packet.m_event_string_code[0] == 80:  # PENA
        # print(packet)
        T = packet.m_event_details.m_penalty
        joueur = LISTE_JOUEURS[T.m_vehicle_idx]
        try:
            if T.m_infringement_type in [7, 27]:
                print(f"Track limit {joueur.get_name()} "
                      f"type {T.m_infringement_type} "
                      f"tour {session.currentLap}")
                if session.Seance == 10:
                    joueur.warnings += 1
        except IndexError:
            print("Erreur pour l'index", T.m_vehicle_idx)
    elif packet.m_event_string_code[3] == 71 and packet.m_event_details.m_start_lights.m_num_lights >= 2:
        session.formationLapDone = True
        print(f"{packet.m_event_details.m_start_lights.m_num_lights} red lights ")
    elif packet.m_event_string_code[0] == 76 and session.formationLapDone:
        print("Lights out !")
        session.formationLapDone = False
        session.startTime = time.time()
        for joueur in LISTE_JOUEURS:
            joueur.S200_reached = False
            joueur.warnings = 0


def update_participants(packet):  # Packet 4
    global MnT_team
    for index in range(22):
        element = packet.m_participants[index]
        joueur = LISTE_JOUEURS[index]
        joueur.numero = element.m_race_number
        joueur.teamId = element.m_team_id
        joueur.aiControlled = element.m_ai_controlled
        if index == MnT_player_index:
            MnT_team = element.m_team_id
        joueur.yourTelemetry = element.m_your_telemetry
        joueur.name = element.m_name.decode("utf-8")
        session.nb_players = packet.m_num_active_cars
        if joueur.name in ['Player', 'Joueur']:
            joueur.name = teams_name_dictionary[joueur.teamId] + "#" + str(joueur.numero) + " "


def update_car_setups(packet):
    array = packet.m_car_setups
    for index in range(22):
        LISTE_JOUEURS[index].setup_array = array[index]
        # print(LISTE_JOUEURS[index].setup_array)


def nothing(packet):
    pass


def update_car_telemetry(packet):  # Packet 6
    for index in range(22):
        element = packet.m_car_telemetry_data[index]
        joueur = LISTE_JOUEURS[index]
        joueur.drs = element.m_drs
        joueur.tyres_temp_inner = element.m_tyres_inner_temperature
        joueur.tyres_temp_surface = element.m_tyres_surface_temperature
        joueur.speed = element.m_speed
        if joueur.speed >= 200 and not joueur.S200_reached:
            print(f"{joueur.position} {joueur.name}  = {time.time() - session.startTime}")
            joueur.S200_reached = True


def update_car_status(packet):  # Packet 7
    for index in range(22):
        element = packet.m_car_status_data[index]
        joueur = LISTE_JOUEURS[index]
        joueur.fuelMix = element.m_fuel_mix
        joueur.fuelRemainingLaps = element.m_fuel_remaining_laps
        joueur.tyresAgeLaps = element.m_tyres_age_laps
        if joueur.tyres != element.m_visual_tyre_compound:
            joueur.tyres = element.m_visual_tyre_compound
            LISTE_CANVAS[index].create_image((12, 12), image=tyres_dictionnary[joueur.tyres])
        joueur.ERS_mode = element.m_ers_deploy_mode
        joueur.ERS_pourcentage = round(element.m_ers_store_energy / 40_000)


def update_car_damage(packet):  # Packet 10
    for index in range(22):
        element = packet.m_car_damage_data[index]
        joueur = LISTE_JOUEURS[index]
        joueur.tyre_wear = list(element.m_tyres_wear)
        joueur.tyre_wear = [round(truc, 2) for truc in joueur.tyre_wear]
        joueur.FrontLeftWingDamage = element.m_front_left_wing_damage
        joueur.FrontRightWingDamage = element.m_front_right_wing_damage
        joueur.rearWingDamage = element.m_rear_wing_damage
        joueur.floorDamage = element.m_floor_damage
        joueur.diffuserDamage = element.m_diffuser_damage
        joueur.sidepodDamage = element.m_sidepod_damage


def create_map():
    if session.trackLength==0:
        return
    build_canvas()
    cmi = 1
    L0 = []
    L = []
    name, d, x_const, z_const = track_dictionary[session.track]
    with open(f"tracks/{name}_2020_racingline.txt", "r") as file:
        for index, line in enumerate(file):
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


def draw_tableau():
    sortedlist = sorted(LISTE_JOUEURS, key=lambda element: element.position)
    try:
        while sortedlist[0].position == 0:
            sortedlist.pop(0)
    except IndexError:
        return
    if clicked_button in [0, 1, 2, 3, 5]:
        for index, joueur in enumerate(sortedlist):
            LISTE_LABELS[index].config(text=joueur.printing(clicked_button, sortedlist, session.Seance),
                                       fg=teams_color_dictionary[joueur.teamId], justify=LEFT)
    elif clicked_button == 6:
        '''for index in range(len(session.weatherList)):
            LISTE_LABELS[index].config(text=session.weatherList[index], fg="black", justify=LEFT)'''
        L = [(a, b) for a, b in zip(F2_teams, updated_standings)]
        L.sort(key=lambda x: x[1], reverse=True)
        for i in range(10):
            LISTE_LABELS[i].config(text=L[i][0] + " : " + str(L[i][1]))
        '''for index in range(len(session.weatherList), len(sortedlist)):
            LISTE_LABELS[index].config(text="", fg="black", justify=LEFT)'''
    elif clicked_button == 4:
        pass
    elif clicked_button == 7:
        for i in range(len(packet_received)):
            t = packetDictionnary[i] + " : " + str(session.packet_received[i]) + "/s"
            LISTE_LABELS[i].config(text=t, fg="black")


def draw_title():
    top_label1.config(text=session.title_display())
    top_label2.config(text=safetyCarStatusDict[session.safetyCarStatus])
    if session.safetyCarStatus == 0:
        top_label2.config(bg="green")
    elif session.safetyCarStatus == 4:
        top_label2.config(bg="red")
    else:
        top_label2.config(bg="yellow")


def draw_tyres():
    sortedlist = sorted(LISTE_JOUEURS, key=lambda element: element.position)
    sortedcanvas = sorted(LISTE_CANVAS, key=lambda element : LISTE_JOUEURS[element[1]].position)
    try:
        while sortedlist[0].position == 0:
            sortedlist.pop(0)
    except IndexError:
        return
    for index in range(len(sortedlist)):
        joueur = sortedlist[index]
        sortedcanvas[index][0].create_image((12, 12), image=tyres_dictionnary[joueur.tyres])


def remove_tyres():
    for index in range(len(LISTE_JOUEURS) - 2):
        LISTE_CANVAS[index][0].delete('all')


def build_canvas():
    global map_canvas
    map_canvas = Canvas(main_frame, bg="pink")
    map_canvas.pack(fill=BOTH, expand=YES)


def check_button(f):
    global clicked_button
    liste_button[clicked_button].config(relief=RAISED)
    clicked_button = f
    liste_button[clicked_button].config(relief=SUNKEN)
    for element in main_frame.winfo_children():
        element.destroy()
    if f in [0, 1, 2, 3, 5]:
        build_labels()
        draw_tyres()
    elif f in [6, 7]:
        build_labels()
        print("hello")
    if f == 4:
        create_map()


def port_selection():
    win = Toplevel()
    win.grab_set()
    win.wm_title("Port Selection")
    Label(win, text="Receiving PORT :", font=("Arial", 16)).grid(row=0, column=0, sticky="we", padx=30)
    e = Entry(win, font=("Arial", 16))
    e.insert(0, dictionnary_settings["port"])
    e.grid(row=1, column=0, padx=30)

    def button():
        global listener
        PORT = e.get()
        if not PORT.isdigit() or not 1000 <= int(PORT) <= 65536:
            Message(win, text="The PORT must be an integer between 1000 and 65536", fg="red", font=("Arial", 16)).grid(
                row=3, column=0)
        else:
            print(int(PORT))
            listener.socket.close()
            listener = Listener(port=int(PORT))
            Label(win, text="").grid(row=3, column=0)
            dictionnary_settings["port"] = str(PORT)
            with open("settings.txt", "w") as f:
                json.dump(dictionnary_settings, f)
            win.destroy()

    win.bind('<Return>', lambda truc: button())
    b = Button(win, text="Confirm", font=("Arial", 16), command=button)
    b.grid(row=2, column=0, pady=10)


def UDP_Redirect():
    win = Toplevel()
    win.grab_set()
    win.wm_title("Port Selection")
    var1 = IntVar(value=dictionnary_settings["redirect_active"])
    checkbutton = Checkbutton(win, text="UDP Redirect", variable=var1, onvalue=1, offvalue=0, font=("Arial", 16))
    checkbutton.grid(row=0, column=0, sticky="W", padx=30, pady=10)
    Label(win, text="IP Address", font=("Arial", 16), justify=LEFT).grid(row=1, column=0, pady=10)
    e1 = Entry(win, font=("Arial", 16))
    e1.insert(0, dictionnary_settings["ip_adress"])
    e1.grid(row=2, column=0)
    Message(win, text="Port", font=("Arial", 16)).grid(row=3, column=0, pady=(10, 5))
    e2 = Entry(win, font=("Arial", 16))
    e2.insert(0, dictionnary_settings["redirect_port"])
    e2.grid(row=4, column=0, padx=30)

    def button():
        global listener
        redirect_port = e2.get()
        if not redirect_port.isdigit() or not 1000 <= int(redirect_port) <= 65536:
            Message(win, text="The PORT must be an integer between 1000 and 65536", fg="red", font=("Arial", 16)).grid(
                row=6, column=0)
        elif not valid_ip_address(e1.get()):
            Label(win, text="IP Address incorrect", fg="red", font=("Arial", 16)).grid(
                row=6, column=0)
        else:
            listener.socket.close()
            listener = Listener(port=int(PORT), redirect=var1, adress=e1.get(), redirect_port=int(e2.get()))
            Label(win, text="").grid(row=3, column=0)

            dictionnary_settings["redirect_active"] = var1.get()
            dictionnary_settings["ip_adress"] = e1.get()
            dictionnary_settings["redirect_port"] = e2.get()
            with open("settings.txt", "w") as f:
                json.dump(dictionnary_settings, f)
            win.destroy()

    win.bind('<Return>', lambda truc: button())
    b = Button(win, text="Confirm", font=("Arial", 16), command=button)
    b.grid(row=5, column=0, pady=10)


def close_window():
    global running
    running = False


def init_window():
    screen.columnconfigure(0, weight=1)
    screen.rowconfigure(0, pad=75)
    screen.rowconfigure(1, weight=1)

    screen.title("Telemetry Application")

    top_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
    main_frame.grid(row=1, column=0, sticky="nsew")

    notebook = ttk.Notebook(main_frame)
    notebook.pack(expand=True, fill="both")

    LISTE_FRAMES.append(Custom_Frame(notebook, "Main Menu"))
    LISTE_FRAMES.append(Custom_Frame(notebook, "Damage"))
    LISTE_FRAMES.append(Custom_Frame(notebook, "Temperatures"))
    LISTE_FRAMES.append(Custom_Frame(notebook, "Laps"))
    LISTE_FRAMES.append(Custom_Frame(notebook, "ERS & Fuel"))
    map = Frame(notebook)
    LISTE_FRAMES.append(map)
    map.pack(expand=True, fill="both")

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
    filemenu.add_command(label="PORT Selection", command=port_selection)
    filemenu.add_command(label="UDP Redirect", command=UDP_Redirect)
    menubar.add_cascade(label="Settings", menu=filemenu)
    screen.config(menu=menubar)


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

'''
indice 7,27,28,29
21 = multiple warnings
'''

WIDTH_POINTS = 6
LISTE_JOUEURS: list[Player] = []
packet_received = [0]*14
last_update = time.time()
LISTE_FRAMES = []
liste_button: list = ["Main Menu", "Damage", "Temperatures", "Laps", "Map", "ERS & Fuel", "Weather Forecast",
                              "Packet Reception"]
clicked_button: int = 0
MnT_player_index = -1
MnT_team = None
L_points = []
with open("settings.txt", "r") as f:
    dictionnary_settings = json.load(f)

top_frame = Frame(screen, bg="green")
main_frame = Frame(screen, bg="blue")

top_label1 = Label(top_frame, text="Course ", bg="purple", font=("Arial", 24), padx=10)
top_label2 = Label(top_frame, text="", bg="yellow", font=("Arial", 24), pady=100, padx=30, width=10)

init_window()

init_20_players()
session: Session = Session()

running = True
PORT = int(dictionnary_settings["port"])
listener = Listener(port=PORT,
                    redirect=dictionnary_settings["redirect_active"],
                    adress=dictionnary_settings["ip_adress"],
                    redirect_port=int(dictionnary_settings["redirect_port"]))


while running:
    a = listener.get()
    if a is not None:
        header, packet = a
        packet_received[header.m_packet_id]+=1
        function_hashmap[header.m_packet_id](packet)
        draw_tableau()

    if time.time() > last_update+1:
        last_update = time.time()
        session.packet_received = packet_received[:]
        packet_received = [0]*14
    screen.update()
    screen.update_idletasks()

listener.socket.close()
quit()
