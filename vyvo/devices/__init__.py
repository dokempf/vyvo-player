import pykka


class MopidyRFIDError(Exception):
    pass


class RFIDDeviceBase:
    def read(self):
        raise NotImplementedError

    def write(self, uri):
        raise NotImplementedError


class DeviceActor(pykka.ThreadingActor)
    """ This actor manages access to the physical device. By only using the
    device through this actor, it is guaranteed that there is no conflict at
    the device level, although different parts of the project access the device.
    """
    def __init__(self, config):
        self.device = None

        if config["vyvo"]["device"] == "diskmock":
            from vyvo.devices.diskmock import DiskMockDevice
            self.device = DiskMockDevice(config)

        if config["vyvo"]["device"] == "rc522":
            from vyvo.devices.rc522 import RC522Device
            self.device = RC522Device(config)

        if self.device is None:
            raise NotImplementedError("Device {} not known".format(config["vyvo"]["device"]))

    def on_receive(self, message):
        if message == "read":
            return self.device.read()
        elif message.startswith("write:"):
            self.device.write(message[7:])
        else:
            raise ValueError("DeviceActor expects 'read' or 'write:<uri>' as message!")
