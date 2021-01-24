import tenseal as ts
import time
from users import DataOwner, DataReceiver
from p2p import Sender, Receiver

class LocalOperations:

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.owner = DataOwner()
        self.result_file = 'result'
        self.flag_file = 'flag'

    def send(file_name):
        sender = Sender(self.address, self.port)
        sender.send(file_name)
        time.sleep(0.001)

    def receive(file_name):
        receiver = Receiver(self.address, self.port)
        receiver.receive(file_name)

    def process(self, x, y):
        flag = False
        self._start(x, y)
        while not flag:
            flag, result = self._listen()
            dec_result = self.owner.decrypt(result)
            if flag:
                return dec_result
            else:
                self._resend(dec_result)

    def _start(self, x, y):
        enc_x = self.owner.encrypt(x)
        enc_y = self.owner.encrypt(y)
        self.owner.package_data(x, 'x_data')
        self.owner.package_data(y, 'y_data')
        self.send('x_data')
        self.send('y_data')

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
        self.port = port

    def send(file_name):
        sender = Sender(self.address, self.port)
        sender.send(file_name)
        time.sleep(0.001)

    def receive(file_name):
        receiver = Receiver(self.address, self.port)
        receiver.receive(file_name)

    def _get_data(self):
        receiver = DataReceiver()
        return receiver.unpack('x_data'), receiver.unpack('y_data')

    def _get_results(self):
        receiver = DataReceiver()
        result = receiver.unpack(self.result_file)
        return result

    def _pack(self, result, flag):
        receiver = DataReceiver()
        receiver.pack_results(results, self.result_file, flag, flag_file)

class EncryptedLinReg(EncryptedOperations):

    def __init__(self, address, port):
        super().__init__(address, port)
        # regression specific params
        self.count = 0 ## Number of operations
        self.beta = 0.5
        self.dbeta = 0
        self.learning_rate = 0.1

    def _calc_loss(self):
        self.err = self.enc_y - self.beta*self.enc_x ## 1D

    def predict(self):
        ## Iterative procedure to get around lack of efficient inverses...
        self.receive('x_data')
        self.receive('y_data')
        self.enc_x, self.enc_y = self._get_data()
        self.err = np.empty(self.enc_x.size())
        for k in range(100): ## change with residual condition later
            try:
                self._calc_loss()
                #print("Loss\t", self.loss)
                self.dbeta = self.err.dot(self.enc_x)
                #print("Grad loss\t", enc_grad_loss)
                #self.dbeta = (2*self.learning_rate/self.N) * enc_grad_loss
                self.beta += self.dbeta
                #print("Beta", self.beta, "Loss\t", self.loss)#, self.beta.decrypt(), self.dbeta.decrypt())
            except:
                ## Local bootstrap
                self._pack(self.beta, False)
                self.send(self.result_file)
                self.send(self.flag_file)
                self.receive(self.result_file)
                self.dbeta = 0

                print("BOOTSTRAP")


            print(f"Beta, round {k}", self.beta)#, "Loss\t", self.loss.decrypt())

        self._pack(self.beta, True)
        self.send(self.result_file)
        self.send(self.flag_file)
