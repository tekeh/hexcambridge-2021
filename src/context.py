import tenseal as ts

class Context:  
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

  def send_package(self, encrypted_data):
    public_serial = self.public_context.serialize()
    data_serial = encrypted_data.serialize()
    return [public_serial, data_serial]

  def receive_package(self, data_serial):
    return CKKSVector.lazy_load(data_serial)
