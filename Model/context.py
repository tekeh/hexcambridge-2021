import tenseal as ts
import numpy as np

class DataOwner:
  def __init__(self, poly_mod_degree=4096, coeff_mod_bit_sizes=[40, 20, 40], global_scale=2**20):
    self.secret_context = ts.context(ts.SCHEME_TYPE.CKKS, poly_mod_degree, -1, coeff_mod_bit_sizes)
    self.secret_context.global_scale = global_scale
    self.secret_context.generate_galois_keys()
    self.public_context = self.secret_context.copy()
    self.public_context.make_context_public()

  def encrypt(self, data):
    return ts.ckks_vector(self.secret_context, data)

  def decrypt(self, data):
    if data.context() == None or data.context().is_public():
      data.link_context(self.secret_context)
    return data.decrypt()

  def _serialize(self, encrypted_vec, filename):
    data_serial = encrypted_vec.serialize()
    with open('{}.bin'.format(data_file), 'wb') as f:
        f.write(data_serial)
        f.close()

  def make_package(self, enc_data, data_file, enc_res=None, res_file=None):
    public_serial = self.public_context.serialize()
    with open('public_key.bin', 'wb') as f:
        f.write(public_serial)
        f.close()
    self._serialize(self, enc_data, data_file)
    if enc_res is not None:
        self._serialize(self, enc_res, res_file)

  def receive_results(self, result_file, flag_file):
      with open('{}.bin'.format(result_file), 'rb') as f:
          res_serial = f.read()
      with open('{}.bin'.format(flag_file), 'rb') as f:
          flag = f.read()
      return flag, ts.ckks_vector_from(self.public_context, res_serial)


class DataReceiver:

    def __init__(self):
        with open('public_key.bin', 'rb') as f:
            public_serial = f.read()
        self.public_context = ts.context_from(public_serial)

    def unpack(self, data_file, flag_file):
        with open('{}.bin'.format(data_file), 'rb') as f:
            data_serial = f.read()
        return ts.ckks_vector_from(self.public_context, data_serial)

    def pack_results(self, results, result_file, flag, flag_file):
        results_serial = results.serialize()
        with open('{}.bin'.format(result_file), 'wb') as f:
            f.write(results_serial)
            f.close()
        with open('{}.bin'.format(flag_file), 'wb') as f:
            f.write(flag)
            f.close()
