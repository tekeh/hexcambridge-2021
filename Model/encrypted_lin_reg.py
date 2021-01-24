import tenseal as ts
from context import DataOwner, DataReceiver

class LocalOperations:

    def __init__(self, data_file, result_file, flag_file, p2p_sender, p2p_receiver):
        self.p2p_sender = p2p_sender
        self.p2p_receiver = p2p_receiver
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
        self.owner.make_package(enc_data, self.data_file)
        self.p2p_sender.send(self.data_file)

    def _listen(self):
        self.p2p_receiver.receive(self.result_file)
        self.p2p_receiver.receive(self.flag_file)
        flag, result = self.owner.receive_results(self.result_file, self.flag_file)
        return flag, result

    def _resend(self, data, dec_result):
        self.owner = DataOwner() # refresh context
        enc_data = self.owner.encrypt(data)
        enc_res = self.owner.encrypt(dec_result)
        self.owner.make_package(enc_data, self.data_file, enc_res, self.result_file)
        self.p2p_sender.send(self.data_file)
        self.p2p_sender.send(self.result_file)



class EncryptedOperations:

    def __init__(self, data_file, result_file, flag_file, p2p_sender, p2p_receiver):
        self.data_file = data_file
        self.result_file = result_file
        self.flag_file = flag_file
        self.p2p_sender = p2p_sender
        self.p2p_receiver = p2p_receiver

    def _get_data(self):
        receiver = DataReceiver()
        return receiver.get_data(self.data_file)

    def _get_data_and_results(self):
        receiver = DataReceiver()
        data = receiver.unpack(self.data_file)
        result = receiver.unpack(self.result_file)
        return data, result

    def _pack(self, result, flag):
        receiver = DataReceiver()
        receiver.pack_results(results, self.result_file, flag, flag_file)

class EncryptedLinReg(EncryptedOperations):
    ## FInds minima via gradient descent
    def __init__(self, data_file, result_file, p2p_node):
        super().__init__(data_file, result_file, p2p_node)

        self.p2p_receiver.receive(self.data_file)

        # regression specific params
        self.count = 0 ## Number of operations
        self.beta = 0.5
        self.dbeta = 0
        self.learning_rate = 0.1
        self.enc_x, self.enc_y = self._get_data()
        self.err = np.empty(self.enc_x.size())
        
    def _calc_loss(self):
        self.err = self.enc_y - self.beta*self.enc_x ## 1D

    def predict(self):
        ## Iterative procedure to get around lack of efficient inverses...
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
                data, self.beta = self._get_data_and_results()
                self.enc_x, self.enc_y = data
                self.dbeta = 0

                print("BOOTSTRAP")


            print(f"Beta, round {k}", self.beta)#, "Loss\t", self.loss.decrypt())

        self._pack(self.beta, True)
        self.p2p_sender.send(self.result_file)
        self.p2p_sender.send(self.flag_file)
