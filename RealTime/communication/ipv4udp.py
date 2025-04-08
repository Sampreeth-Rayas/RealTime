import os
import socket
import threading
import sys
import time
import numpy as np

# Define the server address and ports
HOST = "192.168.33.30"  # Localhost
PORT = 4098
global no_of_packets
global client

packet_size = 1466
header_bytes = 10

file_path = "D:\\Sampreeth\\Project\\mmWaveRadar\\RealTime\\Programs\\bin\\udp_data.bin"
raw_data = []
last_packet = []

server_socket = None

def configure_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, port))
    return server_socket

def process_data():
    global client
    iterator = 0
    #global no_of_packets
    print("Opening the client socket")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("192.168.33.28", 4098))

    waiting_cycle = 0
    print("Will start sending the data")
    while (True):
        raw_data_len = len(raw_data)
        if raw_data_len == 0:
            #print("Raw data length is zero. Closing the client socket")
            time.sleep(0.5)
            continue

        if iterator != 0 : #and iterator == no_of_packets:
            print('Transferred all the data ', iterator, ' raw data len ', raw_data_len)
            client.close()
            break

        if raw_data_len == iterator:
            print(f"Raw data len = iterator : {raw_data_len}")
            if waiting_cycle == 3:
                print("Waiting cycles are completed. Closing the client socket")
                client.close()
                break
            waiting_cycle = waiting_cycle + 1
            time.sleep(0.5)
            continue

        seq_no = int.from_bytes(raw_data[iterator][:4], "little")
        data_len = int.from_bytes(raw_data[iterator][4:8], "little")
        #byte_count = int.from_bytes(raw_data[iterator][8:14], "little")
        #print(f'Sequence No : {seq_no} Data Len : {data_len} Byte Count : {byte_count} Raw Data Len :{raw_data_len} ')
        client.send(raw_data[iterator][header_bytes:])
        iterator = iterator + 1
        #no_of_packets = no_of_packets + 1

def start_server(server_socket):
    global last_packet
    global raw_data
    global no_of_packets
    no_of_packets = 0
    client = configure_client()
    #current_index = 0
    #thread = threading.Thread(target=process_data)
    #thread.start()
    first_packet = False
    no_of_bytes = 0
    while True:
        packet_data = server_socket.recv(4096)
        data_len = len(packet_data)
        no_of_bytes = no_of_bytes + data_len - header_bytes
        if data_len < packet_size:
            packets_count = len(raw_data)
            #last_packet = packet_data
            #update_raw_data(packet_data, client)
            #client.send(packet_data[header_bytes:])
            print(
                f"Data Len {data_len} less than {packet_size}. So assigning last packet. Packet count : {packets_count} + 1. Total : {no_of_bytes}")
            #client.close()
            break

        #update_raw_data(packet_data, client)
        #client.send(packet_data[header_bytes:])

        if first_packet is False:
            #thread.start()
            print("Started the thread")
            first_packet = True
        '''
        seq_no = int.from_bytes(packet_data[:4], "little")
        data_len = int.from_bytes(packet_data[4:8], "little") - current_index
        current_index = int.from_bytes(packet_data[4:8], "little")
        byte_count = int.from_bytes(packet_data[8:14], "little")
        print(f'Sequence No : {seq_no} Data Len : {data_len} Byte Count : {byte_count}')
        client.send(packet_data[14:])
        '''
    #client.close()


def configure_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("192.168.33.28", 4098))
    return client

def update_raw_data(packet_data, client):
    global no_of_packets
    packet_data_len = len(packet_data)
    if  packet_data_len == packet_size:
        #raw_data.append(packet_data[header_bytes:])
        print(f'{no_of_packets} : {packet_data_len}')
        data = packet_data[header_bytes:]
        client.send(data)
        #data_len = len(data)
        #print(f'{no_of_packets} : {data_len}')
        no_of_packets = no_of_packets + 1
        return


    packets_count = int(packet_data_len / packet_size)

    for i in range(packets_count):
        #raw_data.append(packet_data[i+header_bytes:i+packet_size])
        index = i * packet_size
        data = np.array(packet_data[index + header_bytes: index +packet_size])
        data_len = len(packet_data[index + header_bytes: index +packet_size])
        print(f' {packet_data_len}:::{index + header_bytes} ... {index +packet_size} ...  {packet_data_len}-{index} ... {no_of_packets} :{data_len}')
        client.send(data)
        no_of_packets = no_of_packets + 1

    #no_of_packets = no_of_packets + packets_count
'''
def start_udp_server(port):
    global no_of_packets
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, port))
    print(f"UDP server listening on {HOST}:{port}")
    try:
        i = 0
        sum = 0
        while True:
            data = server_socket.recv(4096)
            raw_data.append(data)
            data_len = len(data)
            sum = sum + data_len
            if data_len < 500:
                print("Last packet :", data_len, " :", sum)
                no_of_packets = i
                break
            i = i + 1
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
    finally:
        server_socket.close()
'''

# Create and start a thread for each port


'''
no_of_packets = 0
thread = threading.Thread(target=process_data)
thread.daemon = True
thread.start()


'''
#start_udp_server(PORTS[0])
server = configure_server(PORTS[0])
#client = configure_client()
start_server(server)


#send_data()