import p2p

number = -2566884
number_bin = number.to_bytes(10, byteorder='little', signed=True)
print(number_bin)

sender = p2p.Sender('127.0.0.1', 8080)
sender.open()
sender.send(number_bin)
sender.close()
