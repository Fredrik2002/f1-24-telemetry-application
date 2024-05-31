## F1 23 Telemetry Application

The goal of this project is to summarize the most crucial informations in the most handy way possible. \
The window was created with tkinter & ttkbootstrap

![Telemetry map](https://github.com/Fredrik2002/f1-23-telemetry-application/assets/86866135/7b1ce85e-f57d-4861-b7f5-10bee4ad9b11)

![Telemetry 2](https://github.com/Fredrik2002/f1-23-telemetry-application/assets/86866135/3653b8ae-4604-402a-886b-45e6cf7147d5)

![Telemetry 3](https://github.com/Fredrik2002/f1-23-telemetry-application/assets/86866135/ff73f7f2-b7c2-48e1-b547-4eebc37fae1c)

![Telemetry 4](https://github.com/Fredrik2002/f1-23-telemetry-application/assets/86866135/080b3804-67bd-4c6b-bc9c-970d796546a3)

## Features
* Mini-Map & Mini sectors coloured by the flag status in that section
* All datas regarding ERS, Fuel, Lap Times, Damages, Temperatures, Tyres and more
* Counts warnings taken by each player
* Record time needed for each player to reach 200km/h at the start
* Possibility to redirect datas to another IP address (which can be yourself, if you want 2 different applications to use the same datas)
* Possibility to check how many packets you receive per second

## Usage
1. Make sure all the packages required are installed. They are :
- tkinter
- ttkbootstrap
- PIL \
Run *Telemetry.py*, go to *Settings* on the top left corner, *PORT Selection*, and you can choose the port you want to receive the datas on. \
If you don't have datas to receive, don't worry : run the *utils/sender.py* file, it will send a few datas on port 20777 of your localhost, so you can see what the app looks like

## Project structure
* data_samples : Provides a dataset for test the app with 'fake' data (used by *utils/sender.py*)
* utils :
    * *sender.py* : Send sample datas to a given port and a given IP address
    * draw.py : If you run this file before the beginning of a lap, it will 'draw' the track by saving all of player's car's positions within the given file
    * *receiver.py* : Stores packets received in a list, and stores the list in a file (such as *data_samples/data_2023.txt*). 10min of recording ~= 100 Mo of data, be careful !
    * *serveur.py* Receives datas from different ports and redirect them to direct IP addresses
    * *calculateur.py* : Doesn't work for now
* *Telemetry.py* : Main application you have to run
* *Player.py* & *Session.py* : Classes to represent a player and a session
* *packet_management.py* : Stores the different packets informations into different players and session instances
* *dictionnaries.py* : This is where all the different dictionnaries are stored
* *Custom_Frame.py* : This is where is created the main frame
* *parser2022.py* & *parser2023.py* : Parse the data received to json objects
* *settings.txt* : This files saves the previous connection settings (so you don't have to enter the same port selection and UDP redirection every time). Do not touch unless you know what you are doing

## To do list
* Check glitch in CLM where a car gets in the middle (Removed AFK cars ?)
* Add estimated pit exit position on the map
* Problem with weather Forecast Sample in 100% (Too many samples ?)

