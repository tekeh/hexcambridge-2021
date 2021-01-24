from Model.encrypted_lin_reg import LocalOperations
import tenseal as ts
import numpy as np

N=10
beta_0 = 1

x = np.arange(N, dtype=float)
y = beta_0*x + np.random.normal(size=N, scale=0.8)
x = x

address = '127.0.0.1'
port = 8080

local_ops = LocalOperations(address, port)
print(local_ops.process(x, y))
