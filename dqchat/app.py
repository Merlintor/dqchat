import secrets
from threading import Thread
import os
from diffiehellman.diffiehellman import DiffieHellman

from server import Server
from client import Client
from tor import TorController
from cli_handler import CLIHandler


class App:
    def __init__(self, port=31213):
        self.token = secrets.token_hex()
        self.tor = TorController()
        self.client = Client(self)
        self.server = Server(self)
        
        self.port = port
        
        self.user_id = None
        self.recently_received_message = False # To prevent gap between two recevied messages, since every first incoming message after sending one prints an empty row
        self.is_chatting = False
        
        self.diffieh = DiffieHellman()
        self.diffieh.generate_public_key()
        self.shared_keys = {}
        
        self.chats = {}
        self.active_chat = None

        self.cli_handler = self.setup_cli_handler()

    def resolve_name_of_active_chat(self, active_chat):
        name = self.client.friend_list.get_name_by_onion(active_chat + ".onion")
        return name if type(name) is not type(None) else "???"
    
    def add_chat_as_friend(self, name):
        if (not self.is_chatting):
            print("Cannot add non-exisiting chatpartner to the friendlist!")
            return
        
        self.client.friend_list.add_friend(name, self.active_chat + ".onion")
    
    def on_message(self, data):
        if not self.client.verify_message(data["author"], data["token"]):
            return

        self.chats.setdefault(data["author"], [])
        self.chats[data["author"]].append({
            "content": data["content"],
            "received": True,
        })
        
        if (not self.recently_received_message):
            print()
        print(self.resolve_name_of_active_chat(data["author"]), ">", data["content"])
        self.recently_received_message = True

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
            try:
                user_id = self.client.friend_list.get_onion_by_name(user_id).split(".")[0]
            except:
                print("Unknown user %s!" % (user_id))
                return
        else:
            user_id = user_id.split(".")[0]

        if self.client.get_status(user_id): # receiver online
            print("%s (%s) is currently online!" % (self.resolve_name_of_active_chat(user_id), user_id))
        else: # receiver offline
            print("%s (%s) is currently not online!" % (self.resolve_name_of_active_chat(user_id), user_id))
            return

        self.active_chat = user_id
        
        if user_id not in self.shared_keys.keys():
            print("Exchanging keys ...")
            result = self.client.generate_shared_key(user_id)
            if not result:
                print("Error exchanging keys, is the user online?")
                return
            else:
                print("End to end encryption is setup.")
                
        self.is_chatting = True

        if self.active_chat in self.chats.keys():
            for message in self.chats[self.active_chat]:
                print(self.resolve_name_of_active_chat(user_id) + (" > " if message["received"] else " < ") + message["content"])
        
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
        cli_handler.add_command("/connect", "connect [<nickname>, <onion>] --- Connect to another user by using either the nickname *OR* their .onion domain", self.start_chat, arg_count=1)
        cli_handler.add_command("/addfriend", "addfriend <nickname> <onion> --- Add an user via the .onion domain under a nickname to your friendlist", self.client.friend_list.add_friend, arg_count=2)
        cli_handler.add_command("/removefriend", "removefriend <nickname> --- Remove an user from your friendlist", self.client.friend_list.remove_friend, arg_count=1)
        cli_handler.add_command("/addchat", "addchat <nickname> --- Add the user you are currently chatting with to your friendlist", self.add_chat_as_friend, arg_count=1)
        cli_handler.add_command("/clear", "clear --- Clear the console", self.clear_terminal, arg_count=0)
        cli_handler.add_command("/about", "about --- Display about text", self.about, arg_count=0)
        cli_handler.add_command("/exit", "exit --- Exit current chat to return the main menu", self.exit_chat, arg_count=0)
        cli_handler.add_command("/help", "", cli_handler.print_all_commands, arg_count=1)
        return cli_handler

    def welcome(self):
        print("---------------------")
        print("| Welcome to DQ-TOR |")
        print("---------------------")

    def about(self):
        print("About Placeholder! Pack dein ASCII Art hier rein Schmeffken ;)")
        print("For help use the /help command!")
        print()

    def run(self):
        self.tor.run_tor()
        self.tor.connect()
        self.tor.create_service()
        self.client.configure_proxies()
        self.user_id = self.tor.get_hostname().replace(".onion", "")
        print("Your user id is", self.user_id + ".onion")

        server_thread = Thread(target=self.server.run, kwargs={"port": self.port})
        server_thread.start()
        
        self.clear_terminal()

        self.welcome()
        self.about()

        # Menu Loop
        while True:
            if (self.is_chatting):
                user_in = input(self.resolve_name_of_active_chat(self.active_chat) + " < ")
                
                if (len(user_in) > 0 and user_in[0] != "/"): # Send message if its not a command
                    self.send_message(user_in)
                else:
                    self.cli_handler.handle(user_in)
                
                self.recently_received_message = False
            else:
                user_in = input("$ ")
                self.cli_handler.handle(user_in)
                self.recently_received_message = False

