## F1 23 Telemetry Application

The goal of this project is to summarize the most crucial informations in the most handy way possible. \
The window was created with tkinter & ttkbootstrap

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
* Draw new Australia, Imola, Las Vegas, new Abu Dhabi, Losail
* Check glitch in CLM where a car gets in the middle
* Add estimated pit exit position on the map
* Add tyres type ! (VITAL)


