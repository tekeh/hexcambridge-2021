from encrypted_lin_reg import LocalOperations
import numpy as np


data_file = 'data'
result_file = 'res'
flag_file = 'flag'
address = ''
port=''


x = np.arange(N, dtype=float)
y = learning_rate*(beta_0*x + np.random.normal(size=N, scale=0.8))
x = learning_rate*x

data = np.stack([x,y], axis=0)
local_ops = LocalOperations(data_file, result_file, flag_file, address, port)
local_ops.process(data)
