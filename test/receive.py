import p2p

file_name = 'receive.bin'

receiver = p2p.Receiver(8080)
receiver.receive(file_name)

with open(file_name, 'rb') as f:
  number_bin = f.read()

number = int.from_bytes(number_bin, byteorder='little', signed=True)
print(number)
