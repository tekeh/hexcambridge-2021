import tenseal as ts
import torch
import numpy as np
import matplotlib.pyplot as plt

## Note! Should scale the vectors by the "learning_factor" to circumvent superfluous modulus switching. Allos more calculations to be performed

def test():
    ## Make some fake data to regress to
    N = 10
    beta_0 = 1
    learning_rate = 0.05
    learning_scale = np.sqrt(2*learning_rate/N)
    x = np.arange(N, dtype=float)
    y = learning_rate*(beta_0*x + np.random.normal(size=N, scale=0.8))
    x = learning_rate*x
    plt.scatter(x, y)
    plt.show()

    x_list = x.tolist()
    y_list = y.tolist()
    ## Encrypt
    context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=8192,
            coeff_mod_bit_sizes = [40, 21, 21, 21, 21, 21, 21, 40]
          )
    context.generate_galois_keys()
    context.global_scale = 2**21

    enc_x = ts.ckks_vector(context, x_list)
    enc_y = ts.ckks_vector(context, y_list)

    lin_regressor = EncryptedLinReg(enc_x, enc_y, context)
    #lin_regressor = EncryptedLinReg(x, y, context)
    beta_g = lin_regressor.predict()
    return beta_g

class EncryptedLinReg:
    ## FInds minima via gradient descent
    def __init__(self, enc_x, enc_y, context):
        ## Load the model
        self.N = 10

        self.count = 0 ## Number of operations
        self.dbeta = np.zeros(self.N)
        self.beta = 0.05
        self.learning_rate = 0.1
        self.err = np.ones(self.N)
        self.enc_x = enc_x
        self.enc_y = enc_y
        self.context = context ## Shouldn't be in the final iteration - is just for testing the regression

    def calc_loss(self):
        self.err = self.enc_y - self.beta*self.enc_x ## 1D
        #self.loss = self.err.dot(self.err)

    def predict(self):
        ## Iterative procedure to get around lack of efficient inverses...
        for _ in range(20): ## change with residual condition later
            try:
                self.calc_loss()
                #print("Loss\t", self.loss)
                self.dbeta = self.err.dot(self.enc_x)
                #print("Grad loss\t", enc_grad_loss)
                #self.dbeta = (2*self.learning_rate/self.N) * enc_grad_loss
                self.beta += self.dbeta
                #print("Beta", self.beta, "Loss\t", self.loss)#, self.beta.decrypt(), self.dbeta.decrypt())
                print("Beta", self.beta, self.beta.decrypt(), self.dbeta.decrypt())
            except:
                ## Local bootstrap
                self.enc_x = ts.ckks_vector(self.context, self.enc_x.decrypt())
                self.enc_y = ts.ckks_vector(self.context, self.enc_y.decrypt())


            #print("Beta", self.beta, self.beta.decrypt(), self.dbeta.decrypt())

if __name__ == "__main__":
    test()
