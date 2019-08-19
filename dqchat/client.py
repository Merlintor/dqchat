from requests import Session, Timeout, ConnectionError


class Client(Session):
    def __init__(self, app, proxy_port=9150, scheme="http"):
        super().__init__()
        self.app = app
        self.scheme = scheme
        self.proxies = {
            "http": "socks5h://localhost:%s" % proxy_port,
            "https": "socks5h://localhost:%s" % proxy_port
        }

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
                "content": content
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
