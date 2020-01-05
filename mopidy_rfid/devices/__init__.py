class RFIDDeviceBase:
    def read(self):
        raise NotImplementedError

    def write(self, uri):
        raise NotImplementedError


def select_device(config):
    device = config["rfid"]["device"]

    if device == "diskmock":
        from mopidy_rfid.devices.diskmock import DiskMockDevice

        return DiskMockDevice(config)

    raise NotImplementedError("Device {} not known".format(device))
