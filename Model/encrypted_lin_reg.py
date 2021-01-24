import tenseal as ts
from users import DataOwner, DataReceiver
from p2p import Sender, Receiver

class LocalOperations:

    def __init__(self, data_file, result_file, flag_file, address, port):
        self.p2p_sender = Sender(address, port)
        self.p2p_receiver = Receiver(address, port)
        self.data_file = data_file
        self.result_file = result_file
        self.flag_file = flag_file
        self.owner = DataOwner()

    def process(self, data):
        flag = False
        self._start(data)
        while not flag:
            flag, result = self._listen()
            dec_result = self.owner.decrypt(result)
            if flag:
                return dec_result
            else:
                self._resend(data, dec_result)

    def _start(self, data):
        enc_data = self.owner.encrypt(data)
        self.owner.package_data(enc_data, self.data_file)
        self.p2p_sender.send(self.data_file)

    def _listen(self):
        self.p2p_receiver.receive(self.result_file)
        self.p2p_receiver.receive(self.flag_file)
        flag, result = self.owner.receive_results(self.result_file, self.flag_file)
        return flag, result

    def _resend(self, data, dec_result):
        enc_res = self.owner.encrypt(dec_result)
        self.owner.package_result(enc_res, self.result_file)
        self.p2p_sender.send(self.result_file)



class EncryptedOperations:

    def __init__(self, data_file, result_file, flag_file, address, port):
        self.data_file = data_file
        self.result_file = result_file
        self.flag_file = flag_file
        self.p2p_sender = Sender(address, port)
        self.p2p_receiver = Receiver(address, port)

    def _get_data(self):
        receiver = DataReceiver()
        return receiver.unpack(self.data_file)

    def _get_results(self):
        receiver = DataReceiver()
        result = receiver.unpack(self.result_file)
        return result

    def _pack(self, result, flag):
        receiver = DataReceiver()
        receiver.pack_results(results, self.result_file, flag, flag_file)

class EncryptedLinReg(EncryptedOperations):
    ## FInds minima via gradient descent
    def __init__(self, data_file, result_file, flag_file, address, port):
        super().__init__(data_file, result_file, flag_file, address, port)
        # regression specific params
        self.count = 0 ## Number of operations
        self.beta = 0.5
        self.dbeta = 0
        self.learning_rate = 0.1

    def _calc_loss(self):
        self.err = self.enc_y - self.beta*self.enc_x ## 1D

    def predict(self):
        ## Iterative procedure to get around lack of efficient inverses...
        self.p2p_receiver.receive(self.data_file)
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
                self.p2p_sender.send(self.result_file)
                self.p2p_sender.send(self.flag_file)
                self.p2p_receiver.receive(self.result_file)
                self.dbeta = 0

                print("BOOTSTRAP")


            print(f"Beta, round {k}", self.beta)#, "Loss\t", self.loss.decrypt())

        self._pack(self.beta, True)
        self.p2p_sender.send(self.result_file)
        self.p2p_sender.send(self.flag_file)
