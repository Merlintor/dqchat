import secrets
from threading import Thread
import os

from server import Server
from client import Client
from tor import TorController


class App:
    def __init__(self, port=31213):
        self.token = secrets.token_hex()
        self.client = Client(self)
        self.server = Server(self)
        self.tor = TorController()
        self.user_id = None

        self.port = port

        self.chats = {}
        self.active_chat = None

        self.run()

    def on_message(self, data):
        if not self.client.verify_message(data["author"], data["token"]):
            return

        self.chats.setdefault(data["author"], [])
        self.chats[data["author"]].append({
            "content": data["content"],
            "received": True,
        })
        print(">", data["content"])

    def send_message(self, content):
        self.chats.setdefault(self.active_chat, [])
        self.chats[self.active_chat].append({
            "content": content,
            "received": False,
        })
        self.client.send_message(self.active_chat, content)

    def start_chat(self, user_id):
        self.clear_terminal()
        print("Success, you're now chatting with the user '" + user_id + "'")
        if self.client.get_status(user_id):
            print("The user is currently online!")
        else:
            self.start_menu()
        self.active_chat = user_id
        if self.active_chat in self.chats.keys():
            for message in self.chats[self.active_chat]:
                print(("> " if message["received"] else "") + message["content"])

        while True:
            text = input()
            if text.lower() == "/exit":
                break

            self.send_message(text)

    def clear_terminal(self):
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def start_menu(self):
        while True:
            self.clear_terminal()
            menu_input = input(
                "What do you want to do?\n 1. Chat with a user. \n 2. Edit your contacts.\n 3. Help and support \n")
            if menu_input == "1":
                self.clear_terminal()
                user_id = input("Which user do you want to chat with?\n")
                self.start_chat(user_id.replace(".onion", ""))
            elif menu_input == "2":
                self.clear_terminal()
                pass  # ADD CONTACT BOOK FUNCTIONS
            elif menu_input == "3":
                print(
                    "If you're being thrown back into the menu while trying to chat with a user, "
                    "the user is most likely offline. For support, smd.")

    def run(self):
        self.tor.create_service()
        self.user_id = self.tor.get_hostname().replace(".onion", "")
        print("Your user id is", self.user_id)

        server_thread = Thread(target=self.server.run, kwargs={"port": self.port})
        server_thread.start()
        self.start_menu()
