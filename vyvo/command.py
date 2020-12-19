from mopidy import commands

from vyvo.devices import select_device


class DispatchCommand(commands.Command):
    def __init__(self):
        super(DispatchCommand, self).__init__()
        self.add_child("read", ReadCommand())
        self.add_child("write", WriteCommand())


class ReadCommand(commands.Command):
    def run(self, args, config):
        device = select_device(config)
        uri = device.read()
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
        device = select_device(config)
        device.write(args.uri)
        return 0
