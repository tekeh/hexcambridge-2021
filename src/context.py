import tenseal as ts
import numpy as np

class DataOwner:
  def __init__(self, poly_mod_degree=4096, coeff_mod_bit_sizes=[40, 20, 40], global_scale=2**20):
    self.secret_context = ts.context(ts.SCHEME_TYPE.CKKS, poly_mod_degree, -1, coeff_mod_bit_sizes)
    self.secret_context.global_scale = global_scale
    self.secret_context.generate_galois_keys()
    self.public_context = self.secret_context.copy()
    self.public_context.make_context_public()
    self.public_context_serial = self.public_context.serialize()

  def encrypt(self, data):
    return ts.ckks_vector(self.secret_context, data)

  def decrypt(self, data):
    if data.context() == None or data.context().is_public():
      data.link_context(self.secret_context)
    return data.decrypt()

  def make_package(self, encrypted_data, filename):
    public_serial = self.public_context.serialize()
    data_serial = encrypted_data.serialize()
    with open('{}.bin'.format(filename), 'wb') as f:
        f.write(data_serial)
        f.close()
    with open('public_key.bin', 'wb') as f:
        f.write(public_serial)
        f.close()

class Computer:

    def __init__(self):
        with open('public_key.bin', 'rb') as f:
            public_serial = f.read()
        self.public_context = ts.context_from(public_serial)

    def get_data(self, filename):
        with open('{}.bin'.format(filename), 'rb') as f:
            data_serial = f.read()
        return ts.ckks_vector_from(self.public_context, data_serial)
