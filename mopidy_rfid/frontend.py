import pykka
import time

from mopidy_rfid.devices import select_device


class RFIDFrontend(pykka.ThreadingActor):
    def __init__(self, config, core):
        super(RFIDFrontend, self).__init__()
        self.core = core
        self.poller = RFIDPollingActor.start(self.actor_ref, config)

    def on_start(self):
        self.poller.tell(None)

    def on_stop(self):
        self.poller.stop()

    def on_receive(self, uri):
        self.core.tracklist.clear()
        self.core.tracklist.add(uris=[uri])
        self.core.playback.play()


class RFIDPollingActor(pykka.ThreadingActor):
    def __init__(self, parent, config):
        super(RFIDPollingActor, self).__init__()
        self.parent = parent
        self.device = select_device(config)
        self.current_uri = None

    def on_receive(self, message):
        uri = self.device.read()

        if uri != self.current_uri:
            self.current_uri = uri
            self.parent.tell(uri)

        time.sleep(1)
        self.actor_ref.tell(None)
