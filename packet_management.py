from Session import Session
from Player import Player
from tkinter import *
from dictionnaries import *
import json
from parser2023 import Listener

LISTE_JOUEURS: list[Player] = []
session: Session = Session()

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
    for index in range(22):
        element = packet.m_participants[index]
        joueur = LISTE_JOUEURS[index]
        joueur.numero = element.m_race_number
        joueur.teamId = element.m_team_id
        joueur.aiControlled = element.m_ai_controlled
        joueur.yourTelemetry = element.m_your_telemetry
        joueur.name = element.m_name.decode("utf-8")
        session.nb_players = packet.m_num_active_cars
        if joueur.name in ['Player', 'Joueur']:
            joueur.name = teams_name_dictionary[joueur.teamId] + "#" + str(joueur.numero) + " "

def update_car_setups(packet): # Packet 5
    array = packet.m_car_setups
    for index in range(22):
        LISTE_JOUEURS[index].setup_array = array[index]

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

def nothing(packet):
    pass

def UDP_Redirect(dictionnary_settings, listener, PORT):
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
        redirect_port = e2.get()
        if not redirect_port.isdigit() or not 1000 <= int(redirect_port) <= 65536:
            Message(win, text="The PORT must be an integer between 1000 and 65536", fg="red", font=("Arial", 16)).grid(
                row=6, column=0)
        elif not valid_ip_address(e1.get()):
            Label(win, text="IP Address incorrect", fg="red", font=("Arial", 16)).grid(
                row=6, column=0)
        else:
            listener[0].socket.close()
            listener[0] = Listener(port=int(PORT[0]), redirect=var1, adress=e1.get(), redirect_port=int(e2.get()))
            Label(win, text="").grid(row=3, column=0)

            dictionnary_settings["redirect_active"] = var1.get()
            dictionnary_settings["ip_adress"] = e1.get()
            dictionnary_settings["redirect_port"] = e2.get()
            with open("settings.txt", "w") as f:
                json.dump(dictionnary_settings, f)
            win.destroy()

    win.bind('<Return>', lambda e: button())
    b = Button(win, text="Confirm", font=("Arial", 16), command=button)
    b.grid(row=5, column=0, pady=10)

def port_selection(dictionnary_settings, listener, PORT):
    win = Toplevel()
    win.grab_set()
    win.wm_title("Port Selection")
    Label(win, text="Receiving PORT :", font=("Arial", 16)).grid(row=0, column=0, sticky="we", padx=30)
    e = Entry(win, font=("Arial", 16))
    e.insert(0, dictionnary_settings["port"])
    e.grid(row=1, column=0, padx=30)

    def button():
        PORT[0] = e.get()
        if not PORT[0].isdigit() or not 1000 <= int(PORT[0]) <= 65536:
            Message(win, text="The PORT must be an integer between 1000 and 65536", fg="red", font=("Arial", 16)).grid(
                row=3, column=0)
        else:
            print(int(PORT[0]))
            listener[0].socket.close()
            listener[0] = Listener(port=int(PORT[0]))
            Label(win, text="").grid(row=3, column=0)
            dictionnary_settings["port"] = str(PORT[0])
            with open("settings.txt", "w") as f:
                json.dump(dictionnary_settings, f)
            win.destroy()

    win.bind('<Return>', lambda truc: button())
    b = Button(win, text="Confirm", font=("Arial", 16), command=button)
    b.grid(row=2, column=0, pady=10)