from mopidy import commands

from vyvo.command import (
    read_from_device,
    write_to_device,
)


class DispatchCommand(commands.Command):
    def __init__(self):
        super(DispatchCommand, self).__init__()
        self.add_child("read", ReadCommand())
        self.add_child("write", WriteCommand())


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
