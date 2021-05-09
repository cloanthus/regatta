import socket
import pickle


class Message:
    def __init__(self, messageType, data):
        self.messageType = messageType
        self.data = data

    def print(self):
        print([self.messageType, self.data])

    def read(self):     #? superflous
        return self.data


class Network:
    def __init__(self):
        self.server = "192.168.0.102"
        self.port = 5555
        self.addr = (self.server, self.port)


class Client(Network):
    def __init__(self):
        super().__init__()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def connect(self, clientType):
        try:
            self.client.connect(self.addr)
            self.connected, clientID = pickle.loads(self.client.recv(2048))
            self.send('id', clientType)
            return clientID
        except Exception as e:
            print(e)

    def send(self, messType, data):
        try:
            self.client.sendall(pickle.dumps(Message(messType, data)))
            if messType == 'get':
                return pickle.loads(self.client.recv(2048*4)).read()
            # send a confirmation? is this all handled by sendall?
        except socket.error as e:
            print(e)

    def listen(self):
        try:
            mess = pickle.loads(self.client.recv(2048*4))
            if mess.messageType == 'upd':
                print(mess)
                return mess.data
        except Exception as e:
            print(e)

class Server(Network):
    def __init__(self):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.bind(self.addr)
            print("server started")
        except socket.error as e:
            print(e)
        self.sock.listen(5)
