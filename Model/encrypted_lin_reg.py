import tenseal as ts
import time
from Model.users import DataOwner, DataReceiver
from Model.p2p import Sender, Receiver
import numpy as np
import socket


class LocalOperations:

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.owner = DataOwner()
        self.result_file = 'result'
        self.flag_file = 'flag'
        self.my_address = self.get_my_address()

    def get_my_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        addr = s.getsockname()[0]
        s.close()
        return addr

    def send(self, file_name):
        time.sleep(1.0)
        sender = Sender(self.address, self.port)
        sender.send('{}.bin'.format(file_name))
        time.sleep(1.0)

    def receive(self, file_name):
        receiver = Receiver(self.my_address, self.port)
        receiver.receive('{}.bin'.format(file_name))
        time.sleep(0.5)

    def process(self, x, y):
        flag = False
        self._start(x, y)
        while not flag:
            print('listening')
            flag, result = self._listen()
            dec_result = self.owner.decrypt(result)
            if flag:
                return dec_result
            else:
                self._resend(dec_result)

    def _start(self, x, y):
        print('packaging data..')
        enc_x = self.owner.encrypt(x)
        enc_y = self.owner.encrypt(y)
        self.owner.package_data(enc_x, 'x_data')
        self.owner.package_data(enc_y, 'y_data')
        print('sending data now')
        self.send('x_data')
        self.send('y_data')
        self.send('public_key')
        print('finished sending')

    def _listen(self):
        self.receive(self.result_file)
        self.receive(self.flag_file)
        flag, result = self.owner.receive_results(self.result_file, self.flag_file)
        return flag, result

    def _resend(self, dec_result):
        enc_res = self.owner.encrypt(dec_result)
        self.owner.package_result(enc_res, self.result_file)
        self.send(self.result_file)



class EncryptedOperations:

    def __init__(self, address, port):
        self.result_file = 'result'
        self.flag_file = 'flag'
        self.address = address
        self.my_address = self.get_my_address()
        self.port = port

    def get_my_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        addr = s.getsockname()[0]
        s.close()
        return addr

    def send(self, file_name):
        time.sleep(1.0)
        sender = Sender(self.address, self.port)
        sender.send('{}.bin'.format(file_name))
        time.sleep(1.0)

    def receive(self, file_name):
        receiver = Receiver(self.my_address, self.port)
        receiver.receive('{}.bin'.format(file_name))
        time.sleep(0.5)

    def _get_data(self):
        receiver = DataReceiver()
        return receiver.unpack('x_data'), receiver.unpack('y_data')

    def _get_results(self):
        receiver = DataReceiver()
        result = receiver.unpack(self.result_file)
        return result

    def _pack(self, result, flag):
        receiver = DataReceiver()
        receiver.pack_results(result, self.result_file, flag, self.flag_file)

class EncryptedLinReg(EncryptedOperations):

    def __init__(self, address, port):
        super().__init__(address, port)
        # regression specific params
        self.count = 0 ## Number of operations
        self.beta = 0.5
        self.dbeta = 0
        self.learning_rate = 0.01

    def _calc_loss(self):
        self.err = self.enc_y - self.beta*self.enc_x ## 1D

    def predict(self):
        ## Iterative procedure to get around lack of efficient inverses...
        self.receive('x_data')
        time.sleep(0.1)
        self.receive('y_data')
        time.sleep(0.1)
        self.receive('public_key')
        time.sleep(0.1)
        print('data received')
        self.enc_x, self.enc_y = self._get_data()
        self.copy_enc_x = self.enc_x.copy()
        self.copy_enc_y = self.enc_y.copy()
        self.err = np.empty(self.enc_x.size())
        k = 0
        while k < 10: ## change with residual condition later
            try:
                self._calc_loss()
                self.dbeta = self.err.dot(self.enc_x)
                self.beta += self.dbeta
                print(k)
                k += 1
            except Exception as e:
                print(e)
                ## Local bootstrap
                print('boot-strapping')
                self._pack(self.beta, False)
                self.send(self.result_file)
                self.send(self.flag_file)
                print('finished sending, receiving now')
                self.receive(self.result_file)
                self.beta = self._get_results()
                self.dbeta = 0
                self.enc_x = self.copy_enc_x.copy()
                self.enc_y = self.copy_enc_y.copy()


        self._pack(self.beta, True)
        self.send(self.result_file)
        self.send(self.flag_file)
