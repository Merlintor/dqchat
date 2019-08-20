from flask import Flask, request, Response
import logging

import helpers


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
        shared_key = helpers.get_shared_key(self.app.diffieh, int(request.form["token"]))
        self.app.shared_keys[request.form["user_id"]] = shared_key
        return Response(str(self.app.diffieh.public_key))

    def verify(self):
        token = request.form.get("token")
        if token == self.app.token:
            return Response()

        return Response(status=401)

    def messages(self):
        data = request.form.to_dict()
        try:
            data["content"] = self.app.shared_keys[data["author"]].decrypt(bytes(data["content"], "utf-8")).decode("utf-8")
        except KeyError:
            return Response("No shared token setup", status=400)

        self.app.on_message(data)
        return Response()
