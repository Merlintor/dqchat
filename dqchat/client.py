from requests import Session, Timeout, ConnectionError

from utils import helpers
from utils.logging import logger
from friendlist import FriendList


class Client(Session):
    def __init__(self, app, scheme="http"):
        super().__init__()
        self.app = app
        self.scheme = scheme
        
        self.friend_list = FriendList()
        self.proxies = {}

    def configure_proxies(self):
        self.proxies["http"] = "socks5h://localhost:%s" % self.app.tor.socks_port
        self.proxies["https"] = "socks5h://localhost:%s" % self.app.tor.socks_port

    def generate_shared_key(self, user_id):
        try:
            resp = self.post("%s://%s.onion/key" % (self.scheme, user_id), timeout=10, data={
                "user_id": self.app.user_id,
                "token": self.app.diffieh.public_key
            })

            if resp.status_code == 200:
                shared_key = helpers.get_shared_key(self.app.diffieh, int(resp.text))
                self.app.shared_keys[user_id] = shared_key
                return True

            else:
                return False
        except (Timeout, ConnectionError):
            return False

    def _encrypt_message(self, user_id, data: str):
        shared_key = self.app.shared_keys[user_id]
        if shared_key is None:
            return None

        return shared_key.encrypt(bytes(data, "utf-8"))

    def get_status(self, user_id):
        try:
            resp = self.get("%s://%s.onion/status" % (self.scheme, user_id), timeout=30)
            return resp.status_code == 200
        except (Timeout, ConnectionError):
            return False

    def send_message(self, user_id, content):
        try:
            resp = self.post("%s://%s.onion/messages" % (self.scheme, user_id), timeout=30, data={
                "author": self.app.user_id,
                "token": self.app.token,
                "content": self._encrypt_message(user_id, content)
            })
            if resp.status_code == 400:
                logger.error(resp.text)

            return resp.status_code == 200
        except (Timeout, ConnectionError):
            logger.error("Sending message failed")
            return False

    def verify_message(self, user_id, token):
        try:
            resp = self.post("%s://%s.onion/verify" % (self.scheme, user_id), timeout=30, data={
                "token": token
            })
            return resp.status_code == 200
        except (Timeout, ConnectionError):
            logger.debug("Could not verfy author of received message")
            return False
