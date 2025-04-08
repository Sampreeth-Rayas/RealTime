import os
import socket
import threading
import sys
import time
import numpy as np

# Define the server address and ports
UDP_IP = "192.168.33.30"  # Localhost
UDP_PORT = 4098
NVDIA_IP = "192.168.33.28"
NVDIA_PORT= 4097
PACKET_SIZE = 1466
HEADER_SIZE = 10

class CaptureAndTransmit:
    raw_data = []
    input_iterator = 0
    output_iterator = 0
    data_transfer_completed = False
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((UDP_IP, UDP_PORT))
        print(f"Created Server Socket. IP Address : {UDP_IP} PORT : {UDP_PORT}")

    def receive(self):
        packet_data = self.server_socket.recv(4096)
        CaptureAndTransmit.raw_data.append(packet_data)
        CaptureAndTransmit.input_iterator = CaptureAndTransmit.input_iterator + 1
        #print(":", CaptureAndTransmit.input_iterator)

    def process_and_send(self):
        iterator = 0
        bytes_sent = 0
        while True :
            if CaptureAndTransmit.input_iterator == 0:
                #print("Input iterator is zero")
                time.sleep(0.1)
                continue

            if CaptureAndTransmit.input_iterator == CaptureAndTransmit.output_iterator:
                #print("Input Iterator = Output Iterator :", CaptureAndTransmit.output_iterator)
                time.sleep(0.5)
                if iterator == 4:
                    print("Last packet sent 2 seconds back. Hence breaking")
                    break
                iterator = iterator + 1
                continue

            data_packet = CaptureAndTransmit.raw_data[CaptureAndTransmit.output_iterator]
            data_packet_length = len(data_packet)

            if data_packet_length <= PACKET_SIZE :
                data = CaptureAndTransmit.raw_data[CaptureAndTransmit.output_iterator][HEADER_SIZE:PACKET_SIZE]
                CaptureAndTransmit.client.send(data)
                bytes_sent = bytes_sent + len(data)

            else:
                no_of_packets = int( data_packet_length / PACKET_SIZE)
                for i in range(no_of_packets):
                    index = i * PACKET_SIZE
                    data = CaptureAndTransmit.raw_data[CaptureAndTransmit.output_iterator][index + HEADER_SIZE:index + PACKET_SIZE]
                    CaptureAndTransmit.client.send(data)
                    bytes_sent = bytes_sent + len(data)

            CaptureAndTransmit.output_iterator = CaptureAndTransmit.output_iterator + 1
        print(f"Closing the client socket. Bytes sent {bytes_sent} ")
        CaptureAndTransmit.client.close()
        CaptureAndTransmit.data_transfer_completed = True

CaptureAndTransmit.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CaptureAndTransmit.client.connect((NVDIA_IP, NVDIA_PORT))
print(f"Created Client Socket. IP Address : {NVDIA_IP} PORT : {NVDIA_PORT}")
captureAndTransmit = CaptureAndTransmit()
thread = threading.Thread(target=captureAndTransmit.process_and_send)
thread.daemon = True
print("Starting a thread to sends the data to NVDIA")
thread.start()

while CaptureAndTransmit.data_transfer_completed is False:
    captureAndTransmit.receive()

print("Terminating the thread")
thread.join()
print("Processing completed")