import tenseal as ts
import torch
import numpy as np
import matplotlib.pyplot as plt

## Note! Should scale the vectors by the "learning_factor" to circumvent superfluous modulus switching. Allos more calculations to be performed

def test():
    ## Make some fake data to regress to
    scale = 10**3
    N = 100
    beta_0 = 1
    learning_rate = 0.005
    learning_scale = np.sqrt(2*learning_rate/N)
    x = np.tile(np.arange(10, dtype=float), 10) #10*10=N=100
    y = learning_scale*(beta_0*x + np.random.normal(size=N, scale=0.8))
    x = learning_scale*x
    plt.scatter(x, y)
    plt.show()
    
    x_list = x.tolist()
    y_list = y.tolist()

    ## Encrypt
    context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree = 8192,
            coeff_mod_bit_sizes = [40, 21, 21, 21, 21, 21, 21, 40]
          )

    context.generate_galois_keys()
    context.global_scale = 2**21

    enc_x = ts.ckks_vector(context, x_list)
    enc_y = ts.ckks_vector(context, y_list)

    #lin_regressor = EncryptedLinReg(enc_x, enc_y, context, scale=10**3)
    lin_regressor = EncryptedLinReg(x, y, context)
    beta_g = lin_regressor.predict()
    return beta_g

class EncryptedLinReg:
    ## FInds minima via gradient descent
    def __init__(self, enc_x, enc_y, context):
        ## Load the model 
        self.N = 100
        
        self.count = 0 ## Number of operations
        self.dbeta = np.zeros(self.N)
        self.beta = 0.5
        self.learning_rate = 0.1
        self.err = np.ones(self.N)
        self.enc_x = enc_x
        self.enc_y = enc_y
        self.context = context ## Shouldn't be in the final iteration - is just for testing the regression

    def recalc_context(self):
            self.context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=8192,
            coeff_mod_bit_sizes = [40, 21, 21, 21, 21, 21, 21, 40]
          )
            self.context.generate_galois_keys()
            self.context.global_scale = 2**21

    def calc_loss(self):
        self.err = self.enc_y - self.beta*self.enc_x ## 1D
        #self.loss = self.err.dot(self.err)


    def predict(self):
        ## Iterative procedure to get around lack of efficient inverses...
        for k in range(100): ## change with residual condition later
            try:
                self.calc_loss()
                #print("Loss\t", self.loss)
                self.dbeta = self.err.dot(self.enc_x)
                #print("Grad loss\t", enc_grad_loss)
                #self.dbeta = (2*self.learning_rate/self.N) * enc_grad_loss
                self.beta += self.dbeta
                #print("Beta", self.beta, "Loss\t", self.loss)#, self.beta.decrypt(), self.dbeta.decrypt())
            except:
                ## Local bootstrap
                self.recalc_context()
                self.enc_x = ts.ckks_vector(self.context, self.enc_x.decrypt())
                self.enc_y = ts.ckks_vector(self.context, self.enc_y.decrypt())
                self.beta = ts.ckks_vector(self.context, self.beta.decrypt())
                self.dbeta = 0

                print("BOOTSTRAP")

            print(f"Beta, round {k}", self.beta)#, "Loss\t", self.loss.decrypt())

        
            #print("Beta, round {k}", self.beta, self.dbeta, "Loss\t", self.loss)

if __name__ == "__main__":
    scale = 10**3
    N = 100
    beta_0 = 1
    learning_rate = 0.01
    learning_scale = np.sqrt(2*learning_rate/N)
    x = np.tile(np.arange(10, dtype=float), 10) #10*10=N=100
    y = learning_scale*(beta_0*x + np.random.normal(size=N, scale=0.8))
    x = learning_scale*x
    plt.scatter(x, y)
    plt.show()
    
    x_list = x.tolist()
    y_list = y.tolist()

    ## Encrypt
    context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree = 8192,
            coeff_mod_bit_sizes = [40, 21, 21, 21, 21, 21, 21, 40]
          )

    context.generate_galois_keys()
    context.global_scale = 2**21

    enc_x = ts.ckks_vector(context, x_list)
    enc_y = ts.ckks_vector(context, y_list)

    lin_regressor = EncryptedLinReg(enc_x, enc_y, context)
    #lin_regressor = EncryptedLinReg(x, y, context)
    beta_g = lin_regressor.predict()
#    test()
