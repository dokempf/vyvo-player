from mopidy.config import types
from datetime import timedelta
from pytimeparse import parse


class Timedelta(types.ConfigValue):
    """ Represent a time interval.
    
    This is parsed uding the pytimeparse library which accepts
    many string formats for time intervals ranging between seconds
    and years. Accepted examples are:
    * '10 minutes', '10m', '10:00'
    * '1d10h', '34h', '1 day, 10 hours'
    """

    def deserialize(self, value):
        return timedelta(seconds=parse(types.decode(value)))

    def serialize(self, value, display=False):
        return str(value)
