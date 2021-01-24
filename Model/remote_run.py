from encrypted_lin_reg import EncryptedLinReg
import numpy as np


data_file = 'data'
result_file = 'res'
flag_file = 'flag'
address = ''
port=''


remote_ops = EncryptedLinReg(data_file, result_file, flag_file, address, port)
remote_ops.predict()
