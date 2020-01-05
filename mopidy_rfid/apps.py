from tornado.web import RequestHandler
from mopidy_rfid.devices import select_device

import json


def app_factory(config, core):
    return [
        ("/read/", ReadRequestHandler, {"config": config}),
        ("/write/", WriteRequestHandler, {"config": config}),
    ]


class ReadRequestHandler(RequestHandler):
    def initialize(self, config):
        self.device = select_device(config)

    def get(self):
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(self.device.read()))


class WriteRequestHandler(RequestHandler):
    def initialize(self, config):
        self.device = select_device(config)

    def post(self):
        self.device.write(self.get_argument("uri"))
