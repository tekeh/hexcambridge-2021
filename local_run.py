from Model.encrypted_lin_reg import LocalOperations
import tenseal as ts
import numpy as np

#N=10
#beta_0 = 1
#
#x = np.arange(N, dtype=float)
#y = beta_0*x + np.random.normal(size=N, scale=0.8)
#x = x

def main(x=None, y=None):
    N = 100
    beta_0 = 1
    learning_rate = 0.01
    learning_scale = np.sqrt(2*learning_rate/N)
    x = np.tile(np.arange(10, dtype=float), 10) #10*10=N=100
    y = learning_scale*(beta_0*x + np.random.normal(size=N, scale=0.8))
    x = learning_scale*x
    #plt.scatter(x, y)
    #plt.show()

    #address = '127.0.0.1'
    address = '192.168.0.12'
    port = 8080

    local_ops = LocalOperations(address, port)
    print(local_ops.process(x, y))

if __name__=="__main__":
    main()
