import os
import pykka
import shelve
import time

from datetime import datetime, timedelta
from mopidy import core
from vyvo import logger
from vyvo.devices import DeviceActor
from contextlib import contextmanager


@contextmanager
def resume_shelve(config):
    # A disk-backed dictionary that we use to store time positions
    # that can later be used to resume playback, if our resume policy
    # requires it. We store key value pairs of the following form:
    # track.uri -> (time in ms, time stamp of playback)
    from vyvo import Extension
    filename = os.path.join(Extension.get_data_dir(config), "resume")
    with shelve.open(filename) as resume_shelf:
        yield resume_shelf


class RFIDFrontend(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(RFIDFrontend, self).__init__()
        self.config = config
        self.core = core
        self.user_uri = None
        self.poller = RFIDPollingActor.start(self.actor_ref, config)

        # The timedelta object to decide whether we want to use resume data
        self.resume_threshold = config["vyvo"]["resume_threshold"]

    def _cache_timestamp(self):
        # Extract the following information for our resume policy:
        # * Current track (identified through the URI)
        # * Time position within track
        # * Time stamp of now to apply resume policies
        if self.user_uri is None:
            return
        track = self.core.playback.get_current_track().get()
        if track is not None:
            pos = self.core.playback.get_time_position().get()
            stamp = datetime.utcnow()
            with resume_shelve(self.config) as resume:
                logger.info("Saving a resume timestamp for user URI '{}'".format(self.user_uri))
                resume[self.user_uri] = (track, pos, stamp)

    def on_start(self):
        # This kicks of the recursive polling of the polling actor
        self.poller.tell(None)

    def on_stop(self):
        self._cache_timestamp()
        self.poller.stop()

    def on_receive(self, uri):
        # Cache the timestamp of what we are currently playing
        self._cache_timestamp()

        # Start playback of a new URI by clearing the tracklist,
        # adding the URI and playing it. The clearing part is radical
        # but a design decision of this extension. Note that as a
        # side effect, passing uri=None will stop playback.
        self.user_uri = uri
        self.core.tracklist.clear()
        self.core.tracklist.add(uris=[uri])
        self.core.playback.play()

        if uri is None:
            logger.info("Vyvo stopped playback because the device registered no tag or empty tag.")
        else:
            logger.info("Vyvo requested playback of user URI '{}'".format(uri))

    def track_playback_started(self, tl_track):
        logger.info("Playback of track URI '{}' started".format(tl_track.track.uri))

        # Maybe resume playback where we have left off
        with resume_shelve(self.config) as resume:
            if self.user_uri in resume:
                track, pos, stamp = resume.pop(self.user_uri)
                delta = datetime.utcnow() - stamp
                if delta < self.resume_threshold:
                    # Skip to the correct track
                    if self.core.playback.get_current_track().get() != track:
                        self.core.tracklist.remove({"tlid": [tl_track.tlid]})
                        return

                    # Seek to correct position
                    self.core.playback.seek(pos)
                    logger.info("Seeked position {}ms because of resume policy".format(pos))

        # Restart polling on the polling actor
        self.poller.tell(None)


class RFIDPollingActor(pykka.ThreadingActor):
    def __init__(self, parent, config):
        super(RFIDPollingActor, self).__init__()
        self.parent = parent
        self.interval = config["vyvo"]["polling_interval"] / 1000
        self.device = DeviceActor.start(config)
        self.current_uri = None

    def on_receive(self, message):
        # In debugging, it is often useful to see the polling frequency live
        logger.debug("Polling the vyvo device...")

        # Read URI from device - None means no tag is present
        uri = self.device.ask("read")

        # If no tag was found, we should double check. At least the
        # RC522 produces false negatives once in a while, which result
        # in unwanted restarts of playback
        if uri is None and uri != self.current_uri:
            uri = self.device.ask("read")

        # If we read an empty string, this tag does not hold any data
        if uri == "":
            uri = None

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

    def on_stop(self):
        self.device.stop()
