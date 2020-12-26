from mopidy import commands

from vyvo.command import (
    get_cache_entries,
    read_from_device,
    write_to_device,
)


class DispatchCommand(commands.Command):
    def __init__(self):
        super(DispatchCommand, self).__init__()
        self.add_child("cache", CacheDispatchCommand())
        self.add_child("read", ReadCommand())
        self.add_child("write", WriteCommand())


class CacheDispatchCommand(commands.Command):
    def __init__(self):
        super(CacheDispatchCommand, self).__init__()
        self.add_child("show", CacheShowCommand())


class CacheShowCommand(commands.Command):
    def run(self, args, config):
        for i, entry in get_cache_entries(config).items():
            print("Item #{}".format(i))
            print("  URI: {}".format(entry["uri"]))
            print("  Age: {}".format(entry["delta"]))


class ReadCommand(commands.Command):
    def run(self, args, config):
        uri = read_from_device(config)
        if uri is None:
            print("No URI stored on RFID tag!")
        else:
            print(uri)
        return 0


class WriteCommand(commands.Command):
    def __init__(self):
        super(WriteCommand, self).__init__()
        self.add_argument("uri")

    def run(self, args, config):
        write_to_device(config, args.uri)
        return 0
