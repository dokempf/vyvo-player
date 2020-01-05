import pykka


class RFIDFrontend(pykka.ThreadingActor):
    def __init__(self, config, core):
        super(RFIDFrontend, self).__init__()
        self.core = core
