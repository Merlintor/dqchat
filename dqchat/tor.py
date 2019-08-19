from stem.control import Controller
import os


class TorController:
    def __init__(self, *args, **kwargs):
        self.controller = Controller.from_port(*args, **kwargs)
        self.controller.authenticate()
        self.hidden_service_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "service"
        ).replace("\\", "/")

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


