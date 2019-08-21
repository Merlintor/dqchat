from stem.control import Controller
from stem.process import launch_tor_with_config
import os
import re


class TorController:
    def __init__(self):
        self.socks_port = None
        self.control_port = None

        self.process = None
        self.controller = None
        self.hidden_service_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "tor/service"
        ).replace("\\", "/")

    @staticmethod
    def get_executable_path():
        if os.name == "nt":
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), "tor\\executables\\windows\\tor.exe")

        else:
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), "tor\\executables\\linux\\tor")

    def run_tor(self):
        print("Starting tor ...")
        socks_pattern = re.compile(r"Socks listener listening on port (?P<port>[0-9]+).$")
        control_pattern = re.compile(r"Control listener listening on port (?P<port>[0-9]+).$")

        def get_ports(log_text):
            socks_match = socks_pattern.search(log_text)
            if socks_match is not None:
                self.socks_port = int(socks_match.group("port"))

            control_match = control_pattern.search(log_text)
            if control_match is not None:
                self.control_port = int(control_match.group("port"))

        self.process = launch_tor_with_config({
            "DataDirectory": os.path.join(os.path.dirname(os.path.abspath(__file__)), "tor\\data"),
            "SocksPort": "auto",
            "ControlPort": "auto",
            "DisableNetwork": "0",
            "HiddenServiceStatistics": "0"
        },
            take_ownership=True,
            tor_cmd=self.get_executable_path(),
            init_msg_handler=get_ports
        )

    def connect(self):
        print("Connecting to tor ...")
        self.controller = Controller.from_port(port=self.control_port)
        self.controller.authenticate()

    def create_service(self):
        return self.controller.create_hidden_service(
            self.hidden_service_dir,
            80,
            target_port=31213
        )

    def remove_service(self):
        return self.controller.remove_hidden_service(self.hidden_service_dir)

    def get_hostname(self):
        try:
            with open(os.path.join(self.hidden_service_dir, "hostname")) as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def close(self):
        self.controller.close()
