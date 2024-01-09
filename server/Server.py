import socket
import threading
import pickle
from Query import *


RESULT_HEADER = 2048
PORT = 5050
# SERVER = "192.168.0.104"
SERVER = "192.168.1.16"
ADDR = (SERVER, PORT)

server = socket.socket()
server.bind(ADDR)


def handle_client(connection, address):
    print(f"[NEW CONNECTION] {address} connected.\n")
    
    connected = True
    while connected:
        msg_length = connection.recv(RESULT_HEADER).decode("latin-1")
        if msg_length:
            msg_length = int(msg_length)
            msg = pickle.loads(connection.recv(msg_length))
            print(f"[QUERY] [{address}] {msg}\n")
            result = ""
            print(f"[RECEIVED FUNCTION CALL] {msg}\n")
            try:
                if msg == [[], []]:
                    pass
                elif len(msg[1]) == 0:
                    result = globals()[msg[0]]()
                else:
                    result = globals()[msg[0]](*msg[1])
                
                result = pickle.dumps(result)
                result_length = str(len(result)).encode("latin-1")
                result_length += b' ' * (RESULT_HEADER - len(result_length))
                connection.send(result_length)
                connection.send(result)
                print("[QUERY STATUS] Valid Query\n")
            
            except Exception as e:
                result = pickle.dumps(result)
                result_length = str(len(result)).encode()
                result_length += b' ' * (RESULT_HEADER - len(result_length))
                connection.send(result_length)
                connection.send(result)
                print("[QUERY STATUS] Invalid Query\n")
                print(f"[PROBLEM] {e}")

            
def start():
    server.listen()

    while True:
        connection, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(connection, address))
        thread.start()
        print(f"[ACTIVE CONNECTION] {threading.active_count() - 1}.")


def main():
    print(f"[STARTING] The server started on {SERVER}")
    start()
    
    
if __name__ == "__main__":
    main()
