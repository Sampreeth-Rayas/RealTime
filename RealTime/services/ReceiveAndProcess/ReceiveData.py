import socket
import matplotlib.pyplot as plt
import numpy as np
import time
import threading

CHIRP_LEN = 256
NUM_CHIRPS = 128
NUM_RX_ANTENNA = 4
RANGE_SIZE = CHIRP_LEN
DOPPLER_SIZE = NUM_CHIRPS
CLIENT_PORT = 4095
FRAME_SIZE = (CHIRP_LEN * NUM_CHIRPS)
FRAME_SIZE_ALL_CHANNELS = (NUM_RX_ANTENNA * FRAME_SIZE)
IN_SERVER_PORT = 4097
IN_SERVER_IP_ADDRESS = "192.168.33.28"
NO_OF_FRAMES = 1
PACKET_SIZE = 1466
DOPPLER_PADDING_FACTOR = 2  # Zero-padding factor for Doppler FFT
THRESHOLD_DB = -40  # Threshold in dB to remove weak/aliased signals
SERVER_IP = "192.168.33.29"
SERVER_PORT = 4097


class ReceiveData:
    frames_data = []
    input_iterator = 0
    output_iterator = 0
    data_transfer_completed = False

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((SERVER_IP, SERVER_PORT))
        print("Connected to remote server ", SERVER_IP, ",port ", SERVER_PORT)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((IN_SERVER_IP_ADDRESS, IN_SERVER_PORT))
        print(f"Bind to IP: {IN_SERVER_IP_ADDRESS} Port : {IN_SERVER_PORT}")

    def receive(self):
        print("Listening ...")
        self.server_socket.listen(1)
        conn, addr = self.server_socket.accept()
        print(f"Connection request received from {addr}. Accepted")
        data = bytearray()
        total_bytes = 0
        max_packet_size = PACKET_SIZE * 16
        while (True):
            chunk = conn.recv(max_packet_size)
            chunk_len = len(chunk)
            #print(f'Received {chunk_len} bytes')
            if chunk is None or len(chunk) == 0:
                print(f"Zero byte data received. Some error. So breaking. Length = {len(data)}")
                break

            if chunk_len + total_bytes >= FRAME_SIZE_ALL_CHANNELS:
                #print("Received one frame data :", (chunk_len + total_bytes))
                data.extend(chunk)
                ReceiveData.frames_data.append(data)
                data = bytearray()
                total_bytes = 0
                #print('Completed one frame data.Frame Size:', len(self.frames_data))
                continue

            #print(f"Chunk length {len(chunk)}")
            data.extend(chunk)
            total_bytes = total_bytes + chunk_len

    def process_and_send(self):
        while (True):
            if ReceiveData.frames_data is None or len(ReceiveData.frames_data) == 0:
                #print('Sleeping ....')
                time.sleep(0.1)
                continue

            #print('Started processing the frame')

            raw_data = ReceiveData.frames_data.pop(0)  # raw_data contains 4 franes data, one for each channel
            size = len(raw_data)
            frame_data = []
            for i in range(0, size, 2):
                frame_data.append(complex(raw_data[i], raw_data[i + 1]))

            raw_data = np.array(raw_data).reshape(-1, NUM_CHIRPS, NUM_RX_ANTENNA, CHIRP_LEN)  # 3 dimension arCHIRP_LENray
            range_doppler_map = self.range_doppler_processing(raw_data, NUM_CHIRPS, CHIRP_LEN, DOPPLER_PADDING_FACTOR)

            self.send(range_doppler_map[0])
            #PRK remove this return....
            #return


    def send(self, data):
        print(f'Sending range-doppler. Size {np.array(data).shape}, {data[0][0]}, {data[0][1]}, {data[0][2]}')
        self.client.send(data)


    def range_doppler_processing(self, data, num_chirps, num_samples, doppler_padding_factor):
        # Perform Range FFT (along the fast-time axis, samples)
        data = np.average(data, axis=2)
        range_fft = np.fft.fft(data, axis=-1, n=num_samples)
        range_fft = range_fft[:, :, :num_samples // 2]  # Use one side of FFT (positive frequencies)
        doppler_fft = np.fft.fft(range_fft, axis=1, n=num_chirps * doppler_padding_factor)
        doppler_map = np.fft.fftshift(doppler_fft, axes=1)  # Shift zero frequency to center
        # Compute power for Range-Doppler map
        range_doppler_map = np.abs(doppler_map)
        range_doppler_map = 20 * np.log10(range_doppler_map / np.max(range_doppler_map))  # Normalize and convert to dB
        # range_doppler_map[range_doppler_map < threshold_dB] = threshold_dB
        return range_doppler_map


receiveData = ReceiveData()

thread = threading.Thread(target=receiveData.process_and_send)
thread.daemon = True
print("Starting a thread to sends the data to NVDIA")
thread.start()
receiveData.receive()
