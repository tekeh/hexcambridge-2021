from Model.encrypted_lin_reg import EncryptedLinReg
import tenseal as ts
import numpy as np


address = '127.0.0.1'
port = 8080

remote_ops = EncryptedLinReg(address, port)
remote_ops.predict()
