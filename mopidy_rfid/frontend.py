import pykka
import time

from mopidy import core

from mopidy_rfid.devices import select_device


class RFIDFrontend(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(RFIDFrontend, self).__init__()
        self.core = core
        self.new_uri_arrived = False
        self.poller = RFIDPollingActor.start(self.actor_ref, config)

    def on_start(self):
        # This kicks of the recursive polling of the polling actor
        self.poller.tell(None)

    def on_stop(self):
        self.poller.stop()

    def on_receive(self, uri):
        # Start playback of a new URI by clearing the tracklist,
        # adding the URI and playing it. The clearing part is radical
        # but a design decision of this extension. Note that as a
        # side effect, passing uri=None will stop playback.
        self.new_uri_arrived = True
        self.core.tracklist.clear()
        self.core.tracklist.add(uris=[uri])
        self.core.playback.play()

    def track_playback_started(self, tl_track):
        # This event listener prevents the poller from scanning
        # for new URIs while we are resolving the current URI,
        # which can produce some sorts of ill-formed states.
        self.new_uri_arrived = False
        self.poller.tell(None)


class RFIDPollingActor(pykka.ThreadingActor):
    def __init__(self, parent, config):
        super(RFIDPollingActor, self).__init__()
        self.parent = parent
        self.device = select_device(config)
        self.current_uri = None

    def on_receive(self, message):
        # Read URI from device - None means no tag is present
        uri = self.device.read()

        # If no tag was found, we should double check. At least the
        # RC522 produces false negatives once in a while, which result
        # in unwanted restarts of playback
        if uri is None and uri != self.current_uri:
            uri = self.device.read()

        # If the URI changed, the frontend should start or stop playback
        if uri != self.current_uri:
            self.current_uri = uri
            self.parent.tell(uri)

            # If we started playback, we should stop polling, see below
            if uri is not None:
                return

        # This actor should recursively trigger itself in all cases
        # except the one where we found new media, in which case the
        # frontend will retrigger polling after playback started.
        time.sleep(1)
        self.actor_ref.tell(message)
