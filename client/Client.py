import socket
import pickle


RESULT_HEADER = 2048
PORT = 5050
# SERVER = "192.168.0.104"
SERVER = "192.168.1.16"
ADDR = (SERVER, PORT)

client = socket.socket()
client.connect(ADDR)


class Client:
    def sendQuery(self, function_name, arguments):
        try:
            sending_obj = pickle.dumps([function_name, arguments])
            sending_obj_length = str(len(sending_obj)).encode()
            sending_obj_length += b' ' * (RESULT_HEADER - len(sending_obj_length))
            client.send(sending_obj_length)
            client.send(sending_obj)
            
            result_length = int(client.recv(RESULT_HEADER).decode())
            result = pickle.loads(client.recv(result_length))

            return result # result is a list
        
        except Exception as e:
            print(f"[PROBLEM] {e}")
            return [(0,)]
            # Can create problem if connection is lost from the server
            # then 0 will be shown to the receivers side as sent message
