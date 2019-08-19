import uuid
from threading import Thread
from server import Server
from client import Client


class App:
    def __int__(self):
        self.token = uuid.uuid4()
        self.client = Client(self)

    def on_message(self, data):

        temp = {
            "author": "ghhasiojasioj.onion",
            "token": "asfiohasofoiahsfiohasofoasf",
            "content": "Hallo"
        }

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

    def run(self, port=31213):
        server = Server(self)
        server_thread = Thread(target=server.run, kwargs={"port": port})
        server_thread.start()
        self.input()

