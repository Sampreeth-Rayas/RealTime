import os
import socket
import threading
import sys
import time
import numpy as np

SERVER_IP = "192.168.33.30"
SERVER_PORT = 4097

class RuntimeChart:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((SERVER_IP, SERVER_PORT))

    def send(self, data):
        self.client.send(bytes(data))

    def close(self):
        self.client.close()

sendOutput = SendOutput()
sendOutput.send("Hello server ")
sendOutput.close()