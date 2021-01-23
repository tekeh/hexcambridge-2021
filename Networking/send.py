import p2p

number = 123456
number_bin = bytes(number)

sender = p2p.Sender('127.0.0.1', 8080)
sender.open()
sender.send(number_bin.seek)
sender.close()
