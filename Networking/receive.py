import p2p

receiver = p2p.Receiver(8080)
receiver.open()
number_bin = receiver.receive()
receiver.close()
number = int.from_bytes(number_bin, byteorder='little', signed=True)
print(number)
