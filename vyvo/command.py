import pykka

from vyvo.devices import DeviceActor
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


def read_from_device(config):
    with unique_actor(DeviceActor, config) as device:
        return device.ask("read")


def write_to_device(config, uri):
    with unique_actor(DeviceActor, config) as device:
        return device.ask("write:{}".format(uri))
