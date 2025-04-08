import os
import socket
import threading
import sys
import time

# Define the server address and ports
HOST = "192.168.33.30"  # Localhost
PORTS = [4098]  # List of ports to listen on
iterator = 0

file_path = "D:\\Sampreeth\\Project\\mmWaveRadar\\RealTime\\Programs\\bin\\udp_data.bin"
raw_data =[]
def start_udp_server(port):
    """Function to start a UDP server on a given port."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, port))
    print(f"UDP server listening on {HOST}:{port}")
    #client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #client.connect(("192.168.33.28", 4098))
    file = None
    try:
        i = 0
        sum = 0
        with open(file_path, 'wb') as file:
            while True:
                #data, client_address = server_socket.recvfrom(65536)
                data = server_socket.recv(4096)
                raw_data.append(data)
                #file.write(data)
                data_len = len(data)
                sum = sum + data_len
                if data_len < 500:
                    print(i, " :",  data_len, " :", sum)
                    break
                i = i+1
                #client.sendto(data, ("192.168.33.28", 4098))
                #client.send(data)
                #print(f"Received message on port {port} from {client_address}: {data}")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
    finally:
        if file is not None:
            file.close()
        server_socket.close()
# Create and start a thread for each port
def process_data():
    iterator = 0
    while(True):
        raw_data_len = len(raw_data)
        if raw_data_len == 0:
            time.sleep(0.5)
            continue

        if raw_data_len == iterator:
            time.sleep(0.1)
            continue

        seq_no = int.from_bytes(raw_data[iterator][:4], "little")
        #seq_mno = raw_data[iterator][:4]
        data_len = int.from_bytes(raw_data[iterator][4:8], "little")
        #data_len = raw_data[iterator][4:8]
        byte_count = int.from_bytes(raw_data[iterator][8:14], "little")
        #byte_count = raw_data[iterator][8:14]
        print(f"Len : {raw_data_len} seq_no={seq_no} dataLlen={data_len} bytecount={byte_count}")
        iterator = iterator+1





'''
threads = []
for port in PORTS:
    thread = threading.Thread(target=start_udp_server, args=(port,))
    thread.daemon = True
    thread.start()
    threads.append(thread)

# Keep the main thread running
for thread in threads:
    thread.join()
'''
thread = threading.Thread(target=process_data)
thread.daemon = True
thread.start()
start_udp_server(PORTS[0])
