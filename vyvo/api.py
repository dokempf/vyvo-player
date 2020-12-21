from tornado.web import RequestHandler
from vyvo.devices import DeviceActor

import json
import pykka


def api_factory(config, core):
    return [
        ("/read/", ReadRequestHandler, {"config": config}),
        ("/write/", WriteRequestHandler, {"config": config}),
    ]


class ReadRequestHandler(RequestHandler):
    def initialize(self, config):
        self.device = pykka.ActorRegistry.get_by_class(DeviceActor)[0]

    def get(self):
        self.set_header("Content-type", "application/json")
        self.write(json.dumps({"uri": self.device.ask("read")}))


class WriteRequestHandler(RequestHandler):
    def initialize(self, config):
        self.device = pykka.ActorRegistry.get_by_class(DeviceActor)[0]

    def post(self):
        self.device.ask("write:{}".format(self.get_argument("uri")))
