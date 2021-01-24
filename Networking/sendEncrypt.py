import tenseal as ts
import time
import p2p

# create encryption context
poly_mod_degree = 4096
coeff_mod_bit_sizes = [40, 20, 40]
context = ts.context(ts.SCHEME_TYPE.CKKS, poly_mod_degree, -1, coeff_mod_bit_sizes)
context.global_scale = 2 ** 20
context.generate_galois_keys()

# write serialised vector and context to file and send

vector = [1, 2, 3, 4, 5]
bin_name = 'vectorSend.bin'
context_name = 'contextSend.bin'

vector_enc = ts.ckks_vector(context, vector)
vector_enc_bin = vector_enc.serialize()
context_bin = context.serialize()
with open(bin_name, 'wb') as f:
  f.write(vector_enc_bin)
  f.close()
with open(context_name, 'wb') as f:
  f.write(context_bin)
  f.close()

sender = p2p.Sender('127.0.0.1', 8080)
sender.send(bin_name)
time.sleep(0.001)
sender = p2p.Sender('127.0.0.1', 8080)
sender.send(context_name)

print("Sent vector:", vector)
