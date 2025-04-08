import time
import sys
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from client import *
import datetime

class FileMonitorHandler(FileSystemEventHandler):
    def __init__(self, file_path):
        self.file_path = file_path
        self.processing = False
        self.buffer_size = 65536 #8192
        self.file = None
        self.date_time1 = datetime.datetime.now()
        self.clinet_obj = None
        self.file_path = "G:\\ti\\mmwave_studio_02_01_01_00\\mmWaveStudio\\PostProc\\adc_data_Raw_0.bin"

    def on_any_event(self, event):
        print ('Some event :', event.src_path )
        if event.src_path == self.file_path :
            print('Found the match ....')
            self.read_file()
		

    def on_modified(self, event):
        if self.processing is True:
            return

        self.processing = True
        self.date_time1 = datetime.datetime.now()
        print('start date time :', self.date_time1)
        self.clinet_obj = client()
        if event.src_path == self.file_path:
            print(f"File {self.file_path} has been modified.")
            self.read_file()

    def read_file(self):
        i = 0;
        try:
            with open(self.file_path, 'rb') as self.file:
                while True:
                    #self.date_time1 = datetime.datetime.now()
                    if os.stat(self.file_path).st_size == 0:
                        time.sleep(0.5)
                        continue
                    data = self.file.read(self.buffer_size)
                    if not data:
                        break
                    #self.date_time2 = datetime.datetime.now()
                    '''
                    while len(data) < self.buffer_size :
                        self.file.seek((-1)*len(data), 1)
                        #time.sleep(0.1)
                        data = self.file.read(self.buffer_size)
                    '''
                    self.clinet_obj.send(data)
                    #self.date_time3 = datetime.datetime.now()
                    #i = i + 1
                    #print ('Sent Iterator :', i)
                    #time.sleep(0.0234375)
                    #if i == 20:
                        #break
                    #print('Sent. Iterator :', i, (self.date_time2 -self.date_time1), (self.date_time3 - self.date_time2))
                print("Completd transfer .............")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        finally:
            self.file.close()
            self.clinet_obj.close()

def monitor_file(file_path):
    event_handler = FileMonitorHandler(file_path)
    observer = Observer()
    observer.schedule(event_handler, path="G:\\ti\\mmwave_studio_02_01_01_00\\mmWaveStudio\\PostProc", recursive=False)
    observer.start()
    print(f"Monitoring changes to {file_path}...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping file monitor.")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    file_path_to_monitor = "G:\\ti\\mmwave_studio_02_01_01_00\\mmWaveStudio\\PostProc\\adc_data_Raw_0.bin"
    file_monitor = FileMonitorHandler(file_path_to_monitor)
    #file_monitor.init_serial_io()
    monitor_file(file_path_to_monitor)
