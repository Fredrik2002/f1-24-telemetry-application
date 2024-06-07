## F1 24 Telemetry Application

The goal of this project is to summarize the most crucial informations in the most handy way possible. \
The window was created with tkinter & ttkbootstrap

![Telemetry map](https://github.com/Fredrik2002/f1-23-telemetry-application/assets/86866135/7b1ce85e-f57d-4861-b7f5-10bee4ad9b11)

![Telemetry 2](https://github.com/Fredrik2002/f1-23-telemetry-application/assets/86866135/3653b8ae-4604-402a-886b-45e6cf7147d5)

![Telemetry 3](https://github.com/Fredrik2002/f1-23-telemetry-application/assets/86866135/ff73f7f2-b7c2-48e1-b547-4eebc37fae1c)

![Telemetry 4](https://github.com/Fredrik2002/f1-23-telemetry-application/assets/86866135/080b3804-67bd-4c6b-bc9c-970d796546a3)

## Usage
1. Make sure all the python packages required are installed :
- tkinter
- ttkbootstrap
- PIL
Open a terminal and type `pip install tkinter ttkbootstrap PIL`

2. Run *Telemetry.py*
3. If you do not receive datas on default port (20777), go to *Settings* on the top left corner of the app, *PORT Selection*, and you can choose the port you want to receive the datas on (default on 20777). 


## Project structure
* utils :
    * *sender.py* : Send sample datas to a given port and a given IP address
    * draw.py : If you run this file before the beginning of a lap, it will 'draw' the track by saving all of player's car's positions within the given file
    * *receiver.py* : Stores packets received in a list, and stores the list in a file (such as *data_samples/data_2023.txt*). 10min of recording ~= 100 Mo of data, be careful !
    * *serveur.py* Receives datas from different ports and redirect them to direct IP addresses
    * *calculateur.py* : Doesn't work for now
* __*Telemetry.py* : Main application you have to run__
* *Player.py* & *Session.py* : Classes to represent a player and a session
* *packet_management.py* : Stores the different packets informations into different players and session instances
* *dictionnaries.py* : This is where all the different dictionnaries are stored
* *Custom_Frame.py* : This is where is created the main frame
* *parser202x.py* : Parse the data received for the F1 2x game (default on F1 24)
* *settings.txt* : This files saves the previous connection settings (so you don't have to enter the same port selection and UDP redirection every time). Do not touch unless you know what you are doing

## To do list
* Problem with weather Forecast Sample in 100% (Too many samples ?)

