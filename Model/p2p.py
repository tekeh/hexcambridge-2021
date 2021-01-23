import socket
import logging

class Sender():
  def __init__(self, address, port):
    self.address = address
    self.port = port
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.type = 'sender'
 
  def open(self):
    try:
      self.socket.connect((self.address, self.port))
      logging.info("Connected to {0} on port {1}".format(self.address, self.port))
      print("Connected to {0} on port {1}".format(self.address, self.port))
    except socket.error as err:
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      logging.error("Connection to {0} on port {1} failed".format(self.address, self.port))
      print("Connection to {0} on port {1} failed".format(self.address, self.port))
      raise

  def close(self):
    self.socket.shutdown(1)
    self.socket.close()

  def send(self, file_name):
    self.open()

    with open(file_name, 'rb') as f:
      data_bin = f.read()

    packet_size = len(data_bin)
    header = '{0}:'.format(packet_size)
    header = bytes(header.encode())

    out = bytearray()
    out += header
    out += data_bin

    try:
      self.socket.sendall(out)
      self.close()
    except Exception:
      exit()

class Receiver():
  def __init__(self, port):
    self.address = '127.0.0.1'
    self.port = port
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.type = 'receiver'

  def open(self):
    self.socket.bind((self.address, self.port))
    self.socket.listen(1)
    logging.info("Waiting for a connection...")
    print("Waiting for a connection...")
    self.client_connection, self.client_address = self.socket.accept()
    logging.info("Connected to: {0}".format(self.client_address[0]))
    print("Connected to: {0}".format(self.client_address[0]))

  def close(self):
    self.client_connection.shutdown(1)
    self.client_connection.close()
        
  def receive(self, file_name, socket_buffer_size=1024):
    self.open()

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
          #print(int(length_str))
          length = int(length_str)
          break
        if len(frameBuffer) < length:
          break
        # split off the full message from the remaining bytes
        # leave any remaining bytes in the frameBuffer!
        frameBuffer = frameBuffer[length:]
        break
    with open(file_name, 'wb') as f:
      f.write(frameBuffer)
      f.close()

    self.close()
