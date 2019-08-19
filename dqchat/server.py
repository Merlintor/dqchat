from flask import Flask, request, jsonify, Response


class Server(Flask):
    def __init__(self, app, *args, **kwargs):
        super().__init__(__name__, *args, **kwargs)
        self.app = app

        self.add_url_rule("/status", "status", self.status, methods=["GET"])
        self.add_url_rule("/messages", "messages", self.messages, methods=["POST"])
        self.add_url_rule("/verify", "verify", self.verify, methods=["POST"])

    def status(self):
        return Response()

    def verify(self):
        token = request.form.get("token")
        if token == self.app.token:
            return Response()

        return Response(status=401)

    def messages(self):
        self.app.on_message(request.form)
        return Response()
