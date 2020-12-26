import os
import pykka

from datetime import datetime, timedelta
from vyvo.devices import DeviceActor
from vyvo.frontend import resume_shelve
from contextlib import contextmanager


@contextmanager
def unique_actor(actor_type, config):
    actors = pykka.ActorRegistry.get_by_class(actor_type)
    if len(actors) == 0:
        actor = actor_type.start(config)
        yield actor
        actor.stop()
    else:
        assert len(actors) == 1
        yield actors[0]


def get_cache_entries(config):
    with resume_shelve(config) as resume:
        return {i: {"uri": k, "delta": str(datetime.utcnow() - v[2])} for i, (k, v) in enumerate(sorted(resume.items(), key=lambda i: i[1][2]))}


def read_from_device(config):
    with unique_actor(DeviceActor, config) as device:
        return device.ask("read")


def write_to_device(config, uri):
    with unique_actor(DeviceActor, config) as device:
        return device.ask("write:{}".format(uri))
