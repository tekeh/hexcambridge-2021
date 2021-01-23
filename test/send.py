import p2p

file_name = 'send.bin'
number = -2566884
number_bin = number.to_bytes(10, byteorder='little', signed=True)
with open(file_name, 'wb') as f:
  f.write(number_bin)
  f.close()

sender = p2p.Sender('127.0.0.1', 8080)
sender.send(file_name)
