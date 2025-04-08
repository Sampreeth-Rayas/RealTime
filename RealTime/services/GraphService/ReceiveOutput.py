import socket
import matplotlib.pyplot as plt
import numpy as np

HOST = "192.168.33.29"
PORT = 4097

num_chirps = 128  # Number of chirps per frame
num_rx_antennas = 4  # Number of receiving antennas
num_samples = 256  # Number of samples per chirp

Fs = 5000e3  # Sampling rate in Hz
S = 8e12  # Chirp slope in Hz/s
T_chirp = 56e-3  # Chirp duration in seconds
frame_iterator = 0
window_width = 5
max_len = 65536

#fig, ax = plt.subplots()
time_distance = []
empty_row = [0 for i in range(num_samples)]

#time_distance = [[0.0]*num_samples]*1000
#empty_float_zeros = np.zeros(num_samples, dtype='float32' )
#time_distance = [empty_float_zeros for i in range(1000)]
#time_distance = np.array(time_distance)


class ReceiveOutput:
    #fig = plt.figure()
    fig, ax = plt.subplots()
    firstTime = True
    im = None

    #ReceiveOutput.total_doppler_array = []
    total_doppler_array = [empty_row for i in range(num_chirps)]
    total_doppler_array = np.array(total_doppler_array)
    
    def __init__(self):

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))  # bind accepts 1 object.hence()
        plt.xlabel('Speed (m/s)')
        plt.ylabel('Range (m)')
        plt.title('Cumulative Speed-Range Map')
        #print('Plottig the data now')
        range_resolution = Fs / (2 * S)
        max_range = range_resolution * (num_samples / 2 )
        self.range_bins = np.linspace(0, 100, num_samples // 2)
        self.range_bins = np.flip(self.range_bins)
        doppler_resolution = 1 / (num_chirps * T_chirp )
        max_velocity = doppler_resolution * (num_chirps / 2)
        self.doppler_bins = np.linspace(-max_velocity, max_velocity, num_chirps)


    def receive(self):
        print("Listening to the socket ")
        self.server_socket.listen(1)
        print("Server listen")
        conn, addr = self.server_socket.accept()
        print("Connection request accepted for address ", addr)
        total_len = 0
        data = bytearray()
        frame_no = 1
        range_doppler_array = []
        while (True) :
            range_doppler_array = np.array(range_doppler_array)
            chunk = conn.recv(65536)
            chunk_len = len(chunk)
            print(f'{chunk_len},\n {chunk} ')
            if chunk is None or len(chunk) == 0:
                print(f"Chunk Length = {len(data)}")
                #data.extend(B'$')
                break
            output = np.frombuffer(chunk, dtype=int, offset=0)
            range_doppler_array = [empty_row for j in range(num_chirps)]
            range_doppler_array = np.array(range_doppler_array)
            for i in range(0, len(output), 3):
                u = output[i]
                v = output[i+1]
                w = output[i+2]
                print(f"Object : {u},   {v},   {w}")
                range_doppler_array[u][v]=w

            self.plot_range_doppler_map_with_sampling_freq(range_doppler_array)
            range_doppler_array = []

    def plot_range_doppler_map_with_sampling_freq(self, range_doppler_map):
        #ReceiveOutput.total_doppler_array = np.array(range_doppler_map)
        # Calculate range and Doppler bins
        #range_doppler_map = np.array(range_doppler_map).transpose()

        i_max, j_max = range_doppler_map.shape
        for i in range(i_max):
            for j in range(j_max) :
                if j == 128 :
                    ReceiveOutput.total_doppler_array[i][j] = -130
                elif range_doppler_map[i][j] != 0 and ReceiveOutput.total_doppler_array[i][j] == 0:
                    #if i > 70 and ReceiveOutput.total_doppler_array[i][j] < -80:
                    #if abs(range_doppler_map[i][j]) - abs(j - 128) > 80:
                        #print(f'[{i}, {j}] > 80 {range_doppler_map[i][j]}.2f')
                        #ReceiveOutput.total_doppler_array[i][j] = 0
                    if range_doppler_map[i][j] < -120 :
                        print(f'Abs value > 120 {range_doppler_map[i][j]}.2f')
                        if j > 128:
                            ReceiveOutput.total_doppler_array[i][j] = -120
                        else:
                            ReceiveOutput.total_doppler_array[i][j] = 120
                    elif range_doppler_map[i][j] < -110 :
                        print(f'Abs value > 110 {range_doppler_map[i][j]}.2f')
                        if j > 128:
                            ReceiveOutput.total_doppler_array[i][j] = -110
                        else:
                            ReceiveOutput.total_doppler_array[i][j] = 110

                    elif range_doppler_map[i][j] < -100 :
                        print(f'Abs value > 100 {range_doppler_map[i][j]}.2f')
                        if j > 128:
                            ReceiveOutput.total_doppler_array[i][j] = -100
                        else:
                            ReceiveOutput.total_doppler_array[i][j] = 100
                    elif range_doppler_map[i][j] < -90 :
                        #print(f'Abs value > 90 {range_doppler_map[i][j]}.2f')
                        if j > 128:
                            ReceiveOutput.total_doppler_array[i][j] = 0
                        else:
                            ReceiveOutput.total_doppler_array[i][j] = 0
                    elif range_doppler_map[i][j] < -80 :
                        #print(f'Abs value > 80 {range_doppler_map[i][j]}.2f')
                        if j > 128:
                            ReceiveOutput.total_doppler_array[i][j] = 0
                        else:
                            ReceiveOutput.total_doppler_array[i][j] = 0
                    elif range_doppler_map[i][j] < -70 :
                        #print(f'Abs value > 70 {range_doppler_map[i][j]}.2f')
                        if j > 128:
                            ReceiveOutput.total_doppler_array[i][j] = 0
                        else:
                            ReceiveOutput.total_doppler_array[i][j] = 0
                    else :
                        #print(f'Any Abs value  {range_doppler_map[i][j]}.2f')
                        if j > 128:
                            ReceiveOutput.total_doppler_array[i][j] = 0
                        else:
                            ReceiveOutput.total_doppler_array[i][j] = 0

        if ReceiveOutput.firstTime is True:
            print(f'First time {self.doppler_bins} ')
            ReceiveOutput.im = ReceiveOutput.ax.imshow( ReceiveOutput.total_doppler_array, aspect='auto', extent=[self.doppler_bins[0], self.doppler_bins[-1], self.range_bins[-1], self.range_bins[0]], cmap='jet')
            plt.xlabel('Velocity (m/s)')
            plt.ylabel('Range (m)')
            plt.draw()
            ReceiveOutput.firstTime = False
            plt.pause(0.001)
        else :
            print('Next time....... ', range_doppler_map)
            ReceiveOutput.im.set_data(ReceiveOutput.total_doppler_array)
            plt.draw()
            plt.pause(0.001)
            #ReceiveOutput.fig.canvas.draw()
            #ReceiveOutput.fig.canvas.flush_events()
            #print("Graph refreshed")
            #ReceiveOutput.ax.imshow(range_doppler_map, aspect='auto', extent=[doppler_bins[0], doppler_bins[-1], range_bins[-1], range_bins[0]], cmap='jet')

        #plt.imshow(range_doppler_map, aspect='auto', extent=[doppler_bins[0], doppler_bins[-1], range_bins[-1], range_bins[0]], cmap='jet')
        #plt.imshow(range_doppler_map, aspect='auto', cmap='jet')
        '''
        plt.colorbar(label='')
        plt.xlabel('Speed (m/s)')
        plt.ylabel('Range (m)')
        plt.title('Cumulative Speed-Range Map')
        plt.show()
        '''
receiveOutput = ReceiveOutput()
receiveOutput.receive()
plt.show()