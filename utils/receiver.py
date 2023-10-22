import socket
import pickle
import threading
import time
import os

PORT = 20777
string = ""

socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
socket.bind(('', PORT))
socket.setblocking(False)

PATH = "E:/Data_samples/datas2.txt"

if os.path.isfile(PATH):
    print(f"WARNING : The file {PATH} already exists, it will be overwritten if you continue.")
    chaine = input("Continue ? [y|N]")
    if chaine in ["y", "Y"]:
        print(f"The file {PATH} will be overwritten.")
    else:
        print(f"Please change the PATH variable if you don't want the {PATH} file to be overwritten, and re-run the program.")
        exit(0)

file = open(PATH, 'wb')
file.close()

def main():
    L=[]
    start = time.time()
    while string!="stop" and time.time()<start+10*60:
        try:
            L.append(socket.recv(2048))
        except BlockingIOError:
            pass
    print(f"\nRecording finished : Storing {len(L)} packets in {PATH}, this may take a few time, please wait")
    file = open(PATH, 'wb')
    pickle.dump(L, file)
    file.close()
    print(f"\nDatas stored in {PATH} with success !")
    exit(0)


def inp():
    global string
    while string!="stop":
        string = input("Enter 'stop' to stop the data recording")

t1=threading.Thread(target=main)
t2=threading.Thread(target=inp)
t1.start()
t2.start()




