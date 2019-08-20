from requests import Session, Timeout, ConnectionError
from cryptography.fernet import Fernet
import json
import base64

import helpers


class Client(Session):
    def __init__(self, app, proxy_port=9150, scheme="http"):
        super().__init__()
        self.app = app
        self.scheme = scheme
        self.proxies = {
            "http": "socks5h://localhost:%s" % proxy_port,
            "https": "socks5h://localhost:%s" % proxy_port
        }

    def _get_shared_key(self, user_id):
        if user_id in self.app.shared_keys.keys():
            return self.app.shared_keys[user_id]

        else:
            try:
                resp = self.post("%s://%s.onion/key" % (self.scheme, user_id), timeout=10, data={
                    "user_id": self.app.user_id,
                    "token": self.app.diffieh.public_key
                })

                if resp.status_code == 200:
                    shared_key = helpers.get_shared_key(self.app.diffieh, int(resp.text))
                    self.app.shared_keys[user_id] = shared_key
                    return shared_key

                else:
                    return None
            except (Timeout, ConnectionError):
                return None

    def _encrypt_message(self, user_id, data: str):
        shared_key = self._get_shared_key(user_id)
        if shared_key is None:
            return None

        return shared_key.encrypt(bytes(data, "utf-8"))

    def get_status(self, user_id):
        try:
            resp = self.get("%s://%s.onion/status" % (self.scheme, user_id), timeout=10)
            return resp.status_code == 200
        except (Timeout, ConnectionError):
            return False

    def send_message(self, user_id, content):
        try:
            resp = self.post("%s://%s.onion/messages" % (self.scheme, user_id), timeout=10, data={
                "author": self.app.user_id,
                "token": self.app.token,
                "content": self._encrypt_message(user_id, content)
            })
            return resp.status_code == 200
        except (Timeout, ConnectionError):
            return False

    def verify_message(self, user_id, token):
        try:
            resp = self.post("%s://%s.onion/verify" % (self.scheme, user_id), timeout=10, data={
                "token": token
            })
            return resp.status_code == 200
        except (Timeout, ConnectionError):
            return False
