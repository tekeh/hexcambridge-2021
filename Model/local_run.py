from encrypted_lin_reg import LocalOperations
import numpy as np


def main(x=None,y=None, N=None):
    data_file = 'data'
    result_file = 'res'
    flag_file = 'flag'
    address = ''
    port=''
    N=10

    x = np.arange(N, dtype=float)
    y = beta_0*x + np.random.normal(size=N, scale=0.8)
    x = x

    data = np.stack([x,y], axis=0)
    local_ops = LocalOperations(data_file, result_file, flag_file, address, port)
    local_ops.process(data)

if __name__=="__main__":
    main()
