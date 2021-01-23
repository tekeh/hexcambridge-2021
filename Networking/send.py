import p2p

number = 123
number_bin = bytes([number])
print(number_bin)

sender = p2p.Sender('127.0.0.1', 8080)
sender.open()
sender.send(number_bin)
sender.close()
