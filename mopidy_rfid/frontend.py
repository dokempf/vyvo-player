import pykka
import time

from mopidy import core
from mopidy_rfid.devices import select_device
from pytools.persistent_dict import PersistentDict, NoSuchEntryError


class RFIDFrontend(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(RFIDFrontend, self).__init__()
        self.core = core
        self.new_uri_arrived = False
        self.poller = RFIDPollingActor.start(self.actor_ref, config)

        # A disk-backed dictionary that we use to store time positions
        # that can later be used to resume playback, if our resume policy
        # requires it. We store key value pairs of the following form:
        # track.uri -> (time in ms, time stamp of playback)
        self.resume_dict = PersistentDict(
            "resume_data", container_dir=config["core"]["data_dir"]
        )

    def on_start(self):
        # This kicks of the recursive polling of the polling actor
        self.poller.tell(None)

    def on_stop(self):
        self.poller.stop()

    def on_receive(self, uri):
        # Extract the following information for our resume policy:
        # * Current track (identified through the URI)
        # * Time position within track
        # * Time stamp of now to apply resume policies
        if uri is None:
            track = self.core.playback.get_current_track().get()
            pos = self.core.playback.get_time_position().get()
            stamp = None
            self.resume_dict[track.uri] = (pos, stamp)

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

        # Maybe resume playback where we have left off
        #         track = self.core.playback.get_current_track().get()
        try:
            pos, stamp = self.resume_dict[tl_track.track.uri]
            self.core.playback.seek(pos)
        except NoSuchEntryError:
            pass


class RFIDPollingActor(pykka.ThreadingActor):
    def __init__(self, parent, config):
        super(RFIDPollingActor, self).__init__()
        self.parent = parent
        self.interval = config["rfid"]["polling_interval"] / 1000
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
        time.sleep(self.interval)
        self.actor_ref.tell(message)
