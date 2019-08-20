import secrets
from threading import Thread
import os

from server import Server
from client import Client
from tor import TorController
from cli_handler import CLIHandler

class App:
    def __init__(self, port=31213):
        self.token = secrets.token_hex()
        self.client = Client(self)
        self.server = Server(self)
        self.port = port
        self.tor = TorController()
        self.user_id = None
        self.is_chatting = False
        
        self.chats = {}
        self.active_chat = None

        self.cli_handler = self.setup_cli_handler()
        
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
        
        if (".onion" not in user_id): # Get onion from username
            user_id = self.client.friend_list.get_onion_by_name(user_id)

        if self.client.get_status(user_id): # connected
            print("The user is currently online!")
            print("Success, you're now chatting with the user '" + user_id + "'")
        else: # unreachable
            print("The user is currently not reachable!")
            return

        self.active_chat = user_id
        self.is_chatting = True
        if self.active_chat in self.chats.keys():
            for message in self.chats[self.active_chat]:
                print(("> " if message["received"] else "") + message["content"])

    def exit_chat(self):
        self.active_chat = None
        self.is_chatting = False

    def clear_terminal(self):
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
    
    def setup_cli_handler(self):
        cli_handler = CLIHandler()
        cli_handler.add_command("/say", "say <msg>", print, arg_count=1)
        cli_handler.add_command("/addfriend", "addfriend <nickname> <onion>", self.client.friend_list.add_friend, arg_count=2)
        cli_handler.add_command("/removefriend", "removefriend <nickname>", self.client.friend_list.remove_friend, arg_count=1)
        cli_handler.add_command("/connect", "connect [<nickname>, <onion>]", self.start_chat, arg_count=1)
        cli_handler.add_command("/exit", "exit", self.exit_chat, arg_count=0)
        cli_handler.add_command("/help", "", cli_handler.print_all_commands, arg_count=1)
        return cli_handler

    def run(self):
        self.tor.create_service()
        self.user_id = self.tor.get_hostname().replace(".onion", "")
        print("Your user id is", self.user_id)

        server_thread = Thread(target=self.server.run, kwargs={"port": self.port})
        server_thread.start()
        
        self.clear_terminal()

        # Menu Loop
        while True:
            if (self.is_chatting):
                user_in = input("< ")
                
                if (user_in[0] != "/"): # Send message if its not a command
                    self.send_message(user_in)
                else:
                    self.cli_handler.handle(user_in)
            else:
                user_in = input("$ ")
                self.cli_handler.handle(user_in)
