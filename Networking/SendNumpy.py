#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 11:44:44 2021

@author: jakub
"""

import socket
import logging
import numpy as np
from io import BytesIO

class NumpySocket():
    def __init__(self):
        self.address = 0
        self.port = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.type = None  # server or client

    def startServer(self, address, port):
        self.type = "server"
        self.address = address
        self.port = port
        try:
            self.socket.connect((self.address, self.port))
            logging.info("Connected to {0} on port {1}".format(self.address, self.port))
        except socket.error as err:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logging.error("Connection to {0} on port {1} failed".format(self.address, self.port))
            raise

    def endServer(self):
        self.socket.shutdown(1)
        self.socket.close()

    def sendNumpy(self, frame):
        if self.type is not "server":
            raise ConfigurationError("class not configured as server")

        if not isinstance(frame, np.ndarray):
            raise TypeError("input frame is not a valid numpy array")
        
        f = BytesIO()
        np.savez(f, frame=frame)
        print(frame[0])
        packet_size = len(f.getvalue())
        print (packet_size)
        header = '{0}:'.format(packet_size)
        header = bytes(header.encode())  # prepend length of array
        print(f)
        out = bytearray()
        out += header

        f.seek(0)
        out += f.read()

        try:
            self.socket.sendall(out)
        except Exception:
            exit()

        logging.debug("frame sent")

    def startClient(self, port):
        self.type = "client"
        self.address = ''
        self.port = port

        self.socket.bind((self.address, self.port))
        self.socket.listen(1)
        logging.info("waiting for a connection...")
        self.client_connection, self.client_address = self.socket.accept()
        logging.info("connected to: {0}".format(self.client_address[0]))

    def endClient(self):
        self.client_connection.shutdown(1)
        self.client_connection.close()

    def recieveNumpy(self, socket_buffer_size=1024):
        if self.type is not "client":
            raise ConfigurationError("class not configured as client")

        length = None
        frameBuffer = bytearray()
        while True:
            data = self.client_connection.recv(socket_buffer_size)
            frameBuffer += data
            if len(frameBuffer) == length:
                break
            while True:
                if length is None:
                    if b':' not in frameBuffer:
                        break
                    # remove the length bytes from the front of frameBuffer
                    # leave any remaining bytes in the frameBuffer!
                    length_str, ignored, frameBuffer = frameBuffer.partition(b':')
                    length = int(length_str)
                if len(frameBuffer) < length:
                    break
                # split off the full message from the remaining bytes
                # leave any remaining bytes in the frameBuffer!
                frameBuffer = frameBuffer[length:]
                length = None
                break
        
        frame = np.load(BytesIO(frameBuffer))['frame']
        logging.debug("frame received")
        return frame

def Main():
    host = '127.0.0.1'
    port = 50001
    NS=NumpySocket()
    NS.startServer(host,port)
    OneArr=np.load("Ones.npy")
    NS.sendNumpy(OneArr)
    print(OneArr[0])
    NS.endServer()

if __name__ == '__main__':
    Main()