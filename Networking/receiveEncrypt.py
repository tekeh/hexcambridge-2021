import tenseal as ts
import time
import p2p

bin_name = 'vectorReceive.bin'
context_name = 'contextReceive.bin'

receiver = p2p.Receiver('127.0.0.1', 8080)
receiver.receive(bin_name)
receiver = p2p.Receiver('127.0.0.1', 8080)
receiver.receive(context_name)

with open(bin_name, 'rb') as f:
  vector_enc_bin = f.read()

with open(context_name, 'rb') as f:
  context_bin = f.read()

context = ts.context_from(context_bin)
vector_enc = ts.ckks_vector_from(context, vector_enc_bin)

vector = vector_enc.decrypt()

print("Received vector:", vector)
