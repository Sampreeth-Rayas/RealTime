import socket
import time

HOST = "192.168.33.28"  # Server IP
PORT = 4097  # Server Port
BUFFER_SIZE = 262144
#FILE_PATH = "D:\\ti\\mmwave_studio_02_01_01_00\\mmWaveStudio\\PostProc\\adc_data.bin"  # Path to the large binary file
FILE_PATH = 'D:\\Radar\\From LRDE\\Moving1i1o.bin'
def send_file(filename, host, port):
    window_width = 4
    mul_factor = window_width * 4
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            print(f"Connected to {host}:{port}")
            total_bytes = 0
            with open(filename, "rb") as file:
                iterations = 0
                packet_no = 0
                while (chunk := file.read(BUFFER_SIZE)):

                    if packet_no % mul_factor == 0 or  (packet_no+1) % mul_factor == 0 or (packet_no+2) % mul_factor == 0 or (packet_no+3) % mul_factor == 0:
                        s.sendall(chunk)

                    packet_no = packet_no + 1
                    total_bytes = total_bytes + len(chunk)
                    print(f'Sent {total_bytes} bytes')

            print(f"File transfer completed. Total bytes sent : {total_bytes}")
            s.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    send_file(FILE_PATH, HOST, PORT)