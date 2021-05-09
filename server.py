from _thread import *
from game import Game
from network import *
import time

connCounter = 0
connLookup = {}
viewerLookup = {}
playerLookup = {}


class Client:
    def __init__(self, conn, connID):
        self.conn = conn
        self.connID = connID

    def send(self, messType, messData):
        self.conn.sendall(pickle.dumps(Message(messType, messData)))
        print('DEBUG: sent:', messType, messData)


class Viewer(Client):
    def __init__(self, conn, connID):
        super().__init__(conn, connID)
        viewerLookup.update({connID: self})

    def handle_message(self, mess):
        def give(request):
            switchReq = {'initial': [game.mapPath,
                                     [boat.get_attr() for boat in game.boats],
                                     [buoy.get_attr() for buoy in game.buoys],
                                     game.wind],
                         }
            self.send('give', switchReq[request])

        switchType = {'get': give
                      # 'join':
                      }
        switchType[mess.messageType](mess.data)


class Player(Client):
    def __init__(self, conn, connID):
        super().__init__(conn, connID)
        playerLookup.update({connID: self})
        self.boat = game.create_boat(connID, pos = (8,8))
        print('DEBUG: player created')
        print('DEBUG: ', self.boat)

    def handle_message(self, mess):
        def give(request):
            switchReq = {'moves': self.boat.get_valid_moves(),
                         'colours': [boat.colour for boat in game.boats],
                         'puffs': self.boat.puffCounter,
                         'legs': game.dice.outcome
                         }
            self.send('give', switchReq[request])

        def move(action):
            self.boat.turn(action)
            silentMoves = ['tack', 'roll', 'spin.', 'puff', 'end']
            if action not in silentMoves:
                for viewer in viewerLookup.values():
                    viewer.send('upd', ['boat', self.boat.get_attr()])

        def change(data):
            property, value = data
            if property == 'colour':
                self.boat.colour = value

        switchType = {'get': give,
                      'move': move,
                      'change': change,
                      }
        switchType[mess.messageType](mess.data)


class Umpire(Client):
    pass


def start_server():
    server = "192.168.0.102"
    port = 5555
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((server, port))
        print("server started")
    except socket.error as e:
        print(e)

    sock.listen(5)
    return sock


def threaded_client(connection, connectionID):
    connection.sendall(pickle.dumps([True, connectionID]))
    identified = False
    client = None
    while not identified:
        try:
            message = pickle.loads(connection.recv(2048))
            if not message:
                break
            else:
                if message.messageType == 'id':
                    switchClient = {'viewer': Viewer,
                                    'umpire': Umpire,
                                    'player': Player,
                                    }
                    client = switchClient[message.data](connection, connectionID)
                    print('DEBUG: connected as:', client.__class__.__name__)
                    identified = True
        except Exception as e:
            print(e)
            break
    while True:
        try:
            message = pickle.loads(connection.recv(2048*4))
            if not message:
                break
            else:
                print('DEBUG: received:', message.messageType, message.data)
                client.handle_message(message)
                pass
        except Exception as e:
            print(e)
            break

    print("Lost connection")
    try:
        del client
    except Exception as e:
        print(e)
    connection.close()
    del connLookup[connectionID]


# def test_movement(cat):
#     cat = 1
#     while True:
#         try:
#             for viewer in viewerLookup.values():
#                 viewer.send('upd', ['wind', 1])
#                 viewer.send('upd', ['boat', [0, (10, 10), 3, False, (255, 255, 0)]])
#             print(['wind', 1], ['boat', [0, (10, 10), 3, False, (255, 255, 0)]])
#             time.sleep(2)
#             for viewer in viewerLookup.values():
#                 viewer.send('upd', ['wind', 0])
#                 viewer.send('upd', ['boat', [0, (11, 10), 1, True, (255, 255, 0)]])
#             print(['wind', 0], ['boat', [0, (11, 10), 1, True, (255, 255, 0)]])
#             time.sleep(2)
#         except Exception as e:
#             print(e)


##########################################################################
server = Server()
game = Game('boards/helford.csv')
game.dice.outcome = 3
print(game.dice.outcome)
game.create_boat(500, pos=(10, 11))
for boat in game.boats:
    print(boat)
# game.create_boat(0, (10, 10), 'P', 3, (255, 255, 0))
# start_new_thread(test_movement, (1, ))
while True:
    conn, addr = server.sock.accept()
    print("Connected to:", addr)
    start_new_thread(threaded_client, (conn, connCounter))
    connLookup.update({connCounter: conn})
    connCounter += 1
