import socket
import pickle
import sys
import threading

PORT = 20777
string = ""
m = sys.maxsize-1
socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
socket.bind(('', PORT))
socket.setblocking(False)

file = open('E:/Data_samples/datas.txt', 'wb')
file.close()
print("opened")

def main():
    L=[]
    while len(L)<m and string!="stop":
        try:
            L.append(socket.recv(2048))
        except BlockingIOError:
            pass
    print(len(L))
    file = open('E:/Data_samples/datas.txt', 'wb')
    pickle.dump(L, file)
    file.close()

def inp():
    global string
    while string!="stop":
        string = input("Enter 'stop' to stop the data recording")

t1=threading.Thread(target=main)
t2=threading.Thread(target=inp)
t1.start()
t2.start()




