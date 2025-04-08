import numpy as np
import matplotlib.pyplot as plt
import sys
from matplotlib.animation import FuncAnimation

num_chirps = 128  # Number of chirps per frame
num_rx_antennas = 4  # Number of receiving antennas
num_samples = 256  # Number of samples per chirp
range_doppler_array = []
Fs = 5000e3  # Sampling rate in Hz
S = 8e12  # Chirp slope in Hz/s
T_chirp = 56e-3  # Chirp duration in seconds
frame_iterator = 0
window_width = 5

maximum_abs_val = 5500000

#fig, ax = plt.subplots()
time_distance = []
total_doppler_array = []
#empty_row = [0 for i in range(num_samples)]
empty_row = [0 for i in range(num_samples)]
total_doppler_array = [empty_row for j in range(num_chirps)]
total_doppler_array = np.array(total_doppler_array)

#time_distance = [[0.0]*num_samples]*1000
empty_float_zeros = np.zeros(num_samples, dtype='float32' )
time_distance = [empty_float_zeros for i in range(1000)]
time_distance = np.array(time_distance)




def load_lvds_data(file_path, num_chirps, num_rx_antennas, num_samples):
    # Load LVDS data and reshape according to the radar setup
    # This assumes binary format. Adapt as needed for your LVDS data format.
    raw_data = np.fromfile(file_path, dtype=np.int16)
    print('Data len : ', len(raw_data))
    size = int(len(raw_data))
    data = []
    for i in range(0, size, 2):
        data.append(complex(raw_data[i], raw_data[i+1]))
    return np.array(data).reshape(-1, num_chirps, num_rx_antennas, num_samples)

def range_doppler_processing(data, num_samples, num_chirps, doppler_padding_factor, threshold_dB):
    # Perform Range FFT (along the fast-time axis, samples)
    #print(f'Num Samples = {num_samples}, num chirps:{num_chirps},doppler_padding_factor: {doppler_padding_factor}')
    #print("range_doppler_processing data ", data)
    range_fft = np.fft.fft(data, axis=-1, n=num_samples)
    range_fft = range_fft[:, :, :, :num_samples // 2]  # Use one side of FFT (positive frequencies)
    doppler_fft = np.fft.fft(range_fft, axis=1, n=num_chirps*doppler_padding_factor)
    doppler_map = np.fft.fftshift(doppler_fft, axes=1)  # Shift zero frequency to center
    #print(f'doppler_map ={doppler_map[0][0], doppler_map[0][1], doppler_map[0][2], doppler_map[0][3]}')
    # Compute power for Range-Doppler map
    range_doppler_map = np.abs(doppler_map)
    #max_value = np.max(range_doppler_map)
    max_value = maximum_abs_val
    #print(f'Absolute doppler_map ={range_doppler_map[0][0], range_doppler_map[0][1], range_doppler_map[0][2], range_doppler_map[0][3]}, max value ={max_value}')

    range_doppler_map = 20 * np.log10(range_doppler_map / max_value)  # Normalize and convert to dB
    #print(f'Loggerthemic scaling doppler_map ={range_doppler_map[0][0], range_doppler_map[0][1], range_doppler_map[0][2], range_doppler_map[0][3]}')
    #range_doppler_map[range_doppler_map < threshold_dB] = threshold_dB
    #print('Before returning range_doppler_processing ', range_doppler_map)
    return range_doppler_map

def plot_range_doppler_map_with_sampling_freq(range_doppler_map, num_samples, num_chirps, Fs, S, T_chirp, firstTime, ax, im, rows):
    # Calculate range and Doppler bins
    #print(f'Range dopper received {range_doppler_map}')
    range_resolution = Fs / (2 * S)
    max_range = range_resolution * (num_samples / 2 )
    range_bins = np.linspace(0, 100, num_samples // 2)
    range_bins = np.flip(range_bins)
    doppler_resolution = 1 / (num_chirps * T_chirp )
    max_velocity = doppler_resolution * (num_chirps / 2)
    doppler_bins = np.linspace(-max_velocity, max_velocity, num_chirps)
    range_doppler_map[range_doppler_map < -150 ] = 0
    i_max, j_max = range_doppler_map.shape
    print(f'imax = {i_max}, jmax = {j_max},   shape = {total_doppler_array.shape}')
    for i in range(i_max):
        for j in range(j_max):
            min = range_doppler_map[i][j]
            if min != 0:
                total_doppler_array[i][j] = min
    print(f'Frame iterator {frame_iterator}, rows = {rows}, widnow width={window_width}')
    #if frame_iterator == rows - window_width:
    #print("Iterator == rows - window width")
    plt.title('Range-Doppler Map ' + str(frame_iterator))
    i_max, j_max = total_doppler_array.shape

    for i in range(i_max):
        #print('')
        for j in range(j_max) :
            if j > 127 and j < 129:
                total_doppler_array[i][j] = -130
            elif total_doppler_array[i][j] != 0:
                #if i > 70 and total_doppler_array[i][j] < -80:
                if abs(total_doppler_array[i][j]) - abs(j - 128) > 80:
                    total_doppler_array[i][j] = 0
                elif total_doppler_array[i][j] > -120 :
                    if j > 128:
                        total_doppler_array[i][j] = -120
                    else:
                        total_doppler_array[i][j] = 120
                elif total_doppler_array[i][j] > -110 :
                    if j > 128:
                        total_doppler_array[i][j] = -110
                    else:
                        total_doppler_array[i][j] = 110
                elif total_doppler_array[i][j] > -100 :
                    if j > 128:
                        total_doppler_array[i][j] = -100
                    else:
                        total_doppler_array[i][j] = 100
                elif total_doppler_array[i][j] > -90 :
                    if j > 128:
                        total_doppler_array[i][j] = -90
                    else:
                        total_doppler_array[i][j] = 90
                elif total_doppler_array[i][j] > -80 :
                    if j > 128:
                        total_doppler_array[i][j] = -80
                    else:
                        total_doppler_array[i][j] = 80
                else :
                    if j > 128:
                        total_doppler_array[i][j] = -50
                    else:
                        total_doppler_array[i][j] = 50

        '''
                if total_doppler_array[i][j] != 0 and abs(total_doppler_array[i][j]) != 50 and total_doppler_array[i][j] != -130:
                    speed = -max_velocity + ((j+1)*2*max_velocity/(j_max))
                    distance = (100*(i+1)/(i_max))
                    if speed != 0 and distance != 0:
                        time = int(abs(speed/distance * 1000))
                        if time < 1000 and time_distance[time][0] < 255:
                            #print('[', time, ', ', time_distance[time][0], '] =', speed)
                            time_distance[time][0] = int(time_distance[time][0]) + 1
                            #print('Verify ', time_distance[time][0], ' j=', j, ' : ', total_doppler_array[i][j])
                            jIndex = int(time_distance[time][0])
                            time_distance[time][jIndex] = distance
                            print('Verify :', jIndex, ' Time:', time, ' speed :', speed, ' distance :', distance, end=' ')
                            print(time_distance[time][int(jIndex)])
                
        np.set_printoptions(threshold=sys.maxsize)
        print('Time distance array')
        x_max, y_max = np.array(time_distance).shape
        print('Shape :::',x_max, '  ', y_max )
        x_axis = []
        y_axis = []
        prev_val = 0
        for i in range(x_max) :
            x_axis.append(i/10)
            if time_distance[i][0] == 0:
                y_axis.append(prev_val)
                continue
            j = int(time_distance[i][0])
            print(' ', i, end=' :')
            #x_axis.append(i)
            if abs(prev_val - time_distance[i][1]) < 15:
                prev_val = time_distance[i][1]
            y_axis.append(prev_val)
            for k in range(j+1) :
                print(time_distance[i][k], end =' ')
            print('')

        x_axis = np.array(x_axis)
        y_axis = np.array(y_axis)
        '''

        #print('Trying to plot graph .......    ..........')
        found = False
        for i in range(i_max):
            for j in range(j_max):
                if total_doppler_array[i][j] != 0:
                    found = True
                    break
                    #print(f'{i},{j},{total_doppler_array[i][j]} ', end='')
            #print('')

        if found is False:
            continue

    print('Found some points')
    if firstTime is True:
        #print(f'First time {doppler_bins} ')
        im = ax.imshow(total_doppler_array, aspect='auto', extent=[doppler_bins[0], doppler_bins[-1], range_bins[-1], range_bins[0]], cmap='jet')
        plt.draw()
        firstTime = False
        plt.xlabel('Velocity (m/s)')
        plt.ylabel('Range (m)')
        plt.pause(0.001)
        #plt.show()

    else:
        if im is None:
            #print('Subsequent times But IM is none......')
            im = ax.imshow(total_doppler_array, aspect='auto',
                           extent=[doppler_bins[0], doppler_bins[-1], range_bins[-1], range_bins[0]], cmap='jet')
        else:
            #print('Subsequent times ......')
            im.set_data(total_doppler_array)
        plt.draw()
        plt.pause(0.001)
    return im
    #print('Returning im')
    #return im

# Radar parameters (change these according to your setup)
def process():
    fig, ax = plt.subplots()
    im = None
    firstTime = False

    file_path = 'D:\\Radar\\From LRDE\\Moving1i1o.bin'  # Path to your LVDS data
    # Physical parameters (adjust according to radar system)
    max_range = 100  # in meters
    max_velocity = 30  # in m/sra
    doppler_padding_factor = 2  # Zero-padding factor for Doppler FFT
    threshold_dB = -40  # Threshold in dB to remove weak/aliased signals
    #Load and process data
    data = load_lvds_data(file_path, num_chirps, num_rx_antennas, num_samples)

    #print(f'1 Data {data[0]}, {data[1]}, {data[2]}, {data[3]}, len(data) ')
    range_doppler_map = range_doppler_processing(data, num_samples, num_chirps, doppler_padding_factor, threshold_dB)
    #print(f'2 range_doppler_map {range_doppler_map[0][0][0][0]}, {range_doppler_map[0][0][0][1]}, {range_doppler_map[0][0][0][2]}, {range_doppler_map[0][0][0][3]}, len(data) ')
    #print('Range Doppler matrix ', np.array(range_doppler_map).shape)
    # Plot the Range-Doppler map
    rows, cols, channels, frames = range_doppler_map.shape
    print('Dimensions :', rows, cols, channels, frames)
    range_doppler = []
    zFrames = []
    yFrames = []
    frames_data = []
    range_doppler_map = np.array(range_doppler_map)

    #plt.figure(figsize=(10, 6))

    update_interval = 100
    firstTime = True
    im = None
    #print(f'Rows : {rows}, Window Width : {window_width}')
    print('Iniitial width ', range_doppler_map.shape)
    for i in range(0, rows, 1):
        '''
        yFrames = []
        for j in range (cols):
            zframes = []
            for l in range(frames):
                sum_channel_data = range_doppler_map[i][j][0][l]  + range_doppler_map[i][j][1][l] + range_doppler_map[i][j][2][l] + range_doppler_map[i][j][3][l]
                zframes.append(sum_channel_data)
            yFrames.append(zframes)

        range_doppler_array = np.array(yFrames)
        '''
        range_doppler_array = np.sum(range_doppler_map[i], axis=1)
        frame_iterator = i
        print('Dim2 = ', range_doppler_array.shape)
        #print(f'{i} range_doppler_array {range_doppler_array[0][0]}, {range_doppler_array[0][1]}, {range_doppler_array[0][2]}, {range_doppler_array[0][3]}, len(data) ')

        range_resolution = Fs / (2 * S)
        max_range = range_resolution * (num_samples / 2 )
        range_bins = np.linspace(0, 100, num_samples // 2)
        range_bins = np.flip(range_bins)
        doppler_resolution = 1 / (num_chirps * T_chirp )
        max_velocity = doppler_resolution * (num_chirps / 2)
        doppler_bins = np.linspace(-max_velocity, max_velocity, num_chirps)
        print(f"Before calling plot_range_doppler_map_with_sampling_freq {num_samples} {num_chirps}, {rows}")
        im = plot_range_doppler_map_with_sampling_freq(np.transpose(range_doppler_array), num_samples, num_chirps, Fs, S,
                                                  T_chirp, firstTime, ax, im, rows)
        firstTime = False
    plt.show()


process()