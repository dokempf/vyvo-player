from mopidy import commands

from vyvo.devices import DeviceActor


class DispatchCommand(commands.Command):
    def __init__(self):
        super(DispatchCommand, self).__init__()
        self.add_child("read", ReadCommand())
        self.add_child("write", WriteCommand())


class ReadCommand(commands.Command):
    def run(self, args, config):
        device = DeviceActor.start(config)
        uri = device.ask("read")
        if uri is None:
            print("No URI stored on RFID tag!")
        else:
            print(uri)
        device.stop()
        return 0


class WriteCommand(commands.Command):
    def __init__(self):
        super(WriteCommand, self).__init__()
        self.add_argument("uri")

    def run(self, args, config):
        device = DeviceActor.start(config)
        device.ask("write:{}".format(args.uri))
        device.stop()
        return 0
