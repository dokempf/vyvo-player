from tornado.web import RequestHandler
from vyvo.command import (
    read_from_device,
    write_to_device,
)

import json


def api_factory(config, core):
    return [
        ("/read/", ReadRequestHandler, {"config": config}),
        ("/write/", WriteRequestHandler, {"config": config}),
    ]


class ReadRequestHandler(RequestHandler):
    def initialize(self, config):
        self.config = config

    def get(self):
        self.set_header("Content-type", "application/json")
        self.write(json.dumps({"uri": read_from_device(self.config)}))


class WriteRequestHandler(RequestHandler):
    def initialize(self, config):
        self.config = config

    def post(self):
        write_to_device(self.config, self.get_argument("uri"))
