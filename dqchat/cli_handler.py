class CLIHandler():
    commands = []

    def add_command(self, name, help_text, bind_func, arg_count=1):
        command = {"name": name, "help_text": help_text, 
                   "bind_func": bind_func, "arg_count": arg_count}
        self.commands.append(command)

    def handle(self, cli_args):
        cli_args = cli_args.split(" ")
        if (len(cli_args) < 1):
            print("Invalid number of arguments!")
            return
                
        command_available = False
        for command in self.commands:
            if (command["name"] == cli_args[0]):
                command_available = True
                try:
                    command["bind_func"](*cli_args[1:1+command["arg_count"]])
                except:
                    print("Inavlid command!")
        
        if (not command_available):
            print("Invalid command '" + cli_args[0] + "'")

    def print_all_commands(self, flags=[]):
        print()

        print("Available Commands")
        for command in self.commands:
            print(command["help_text"])