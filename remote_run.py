from Model.encrypted_lin_reg import EncryptedLinReg
import tenseal as ts
import numpy as np


def main():
    address = '192.168.0.12'
    port = 8080

    remote_ops = EncryptedLinReg(address, port)
    remote_ops.predict()

if __name__=="__main__":
    main()
