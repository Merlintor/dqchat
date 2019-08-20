from flask import Flask, request, jsonify, Response
from cryptography.fernet import Fernet
import logging
import json
import base64


class Server(Flask):
    def __init__(self, app, *args, **kwargs):
        super().__init__(__name__, *args, **kwargs)
        self.app = app

        self.add_url_rule("/status", "status", self.status, methods=["GET"])
        self.add_url_rule("/key", "key", self.key, methods=["POST"])
        self.add_url_rule("/messages", "messages", self.messages, methods=["POST"])
        self.add_url_rule("/verify", "verify", self.verify, methods=["POST"])

        logging.getLogger('werkzeug').setLevel(logging.ERROR)

    def status(self):
        return Response("Online")

    def key(self):
        data = request.form

        self.app.diffieh.generate_shared_secret(int(data["token"]), echo_return_key=True)
        self.app.shared_keys[data["user_id"]] = Fernet(base64.urlsafe_b64encode(bytes(self.app.diffieh.shared_key[:32], "utf-8")))
        return Response(str(self.app.diffieh.public_key))

    def verify(self):
        token = request.form.get("token")
        if token == self.app.token:
            return Response()

        return Response(status=401)

    def messages(self):
        data = dict(request.form)
        print(data)
        data["content"] = str(self.app.shared_keys[data["author"]].decrypt(bytes(data["content"], "utf-8")))
        print(data)
        self.app.on_message(data)
        return Response()
