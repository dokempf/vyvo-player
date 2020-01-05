import pykka

from mopidy_rfid.devices import select_device


class RFIDFrontend(pykka.ThreadingActor):
    def __init__(self, config, core):
        super(RFIDFrontend, self).__init__()
        self.core = core

        self.device = select_device(config)
