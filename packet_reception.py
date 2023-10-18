import socket
import time

PORT = 20755
FREQ = 60
socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
socket.bind(('', PORT))
last_update = 0
current_packet_freq = [0] * 12
theorical_packet_freq = [FREQ, 2, FREQ,0,0, 2, FREQ, FREQ, 0, 0, 2, 20]

while True:
    packet = socket.recv(2048)
    current_packet_freq[packet[5]]+=1
    #print(packet)
    if last_update+1<time.time():
        current_packet_freq[3:5] = [0,0]
        print(f"Packet loss :{round((1-(sum(current_packet_freq)/sum(theorical_packet_freq)))*100,1)} %", )
        for current, theorique in zip(current_packet_freq, theorical_packet_freq):
            print(f"{current}/{theorique}")
        last_update = time.time()
        current_packet_freq = [0] * 12

