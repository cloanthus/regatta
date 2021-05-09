import socket
from _thread import *
import pickle
import time

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


def threaded_client(connection):
    while True:
        try:
            time.sleep(1)
            connection.sendall(pickle.dumps([0,1,2]))
            # message = pickle.loads(connection.recv(2048*4))
            # if not message:
            #     break
            # else:
            #     # handle incoming messages from the client
            #     pass
        except Exception as e:
            print(e)
            break
    connection.close()


###################################################################################################
s = start_server()
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    start_new_thread(threaded_client, (conn, ))
    # connLookup.update({connCounter: conn})
    # connCounter += 1