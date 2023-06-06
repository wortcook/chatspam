import socket

import Filter
import numpy as np
import pandas as pd


class Server:
    def __init__(self, host = 'localhost', port = 8123):
        self.host = host
        self.port = port
        df = pd.read_csv('../../data/spam_ham_prompts.csv')

        print(df)

        self.payload = Filter.fit(df,df['label'])


    def Filter(self, message):
        return Filter.predict(self.payload,message)


    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Server started at {self.host}:{self.port}. Waiting for connections...")
            while True:
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        filtered_data = self.Filter(data.decode())
                        conn.sendall(filtered_data.encode())

if __name__ == "__main__":
    server = Server('localhost', 8123)
    server.start()
