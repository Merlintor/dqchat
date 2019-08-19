import secrets
from threading import Thread
from server import Server
from client import Client


class App:
    def __init__(self, port=31213):
        self.token = secrets.token_hex()
        self.client = Client(self)
        self.server = Server(self)
        self.port = port

    def on_message(self, data):
        print(data)

    def display_message(self):
        pass

    def send_message(self, text):
        #TODO Send Message
        pass

    def input(self):
        while True:
            text_message = input()
            print(text_message)
            self.send_message(text_message)

    def run(self):
        server_thread = Thread(target=self.server.run, kwargs={"port": self.port})
        server_thread.start()
        self.input()

