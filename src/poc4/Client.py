import socket

class Client:
    def __init__(self, server_host='localhost', server_port=8123):
        self.server_host = server_host
        self.server_port = server_port

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.server_host, self.server_port))
            print(f"Connected to server at {self.server_host}:{self.server_port}.")
            while True:
                message = input("Enter a message (or 'quit' to exit): ")
                if message.lower() == 'quit':
                    break
                s.sendall(message.encode())
                data = s.recv(1024)
                print('Received from server:', data.decode())

                #now check with open ai
                #if open ai says it is spam, then send a message to the server to add it to the spam list
                #if open ai says it is ham, then send a message to the server to add it to the ham list

                

if __name__ == "__main__":
    client = Client('localhost', 8123)
    client.start()
