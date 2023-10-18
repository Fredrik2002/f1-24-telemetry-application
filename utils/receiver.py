import socket
import pickle

PORT = 20776
socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
socket.bind(('', PORT))

L=[]
while len(L)<10000:
    L.append(socket.recv(2048))
    
file = open('datas.txt', 'wb')
pickle.dump(L, file)
file.close()



