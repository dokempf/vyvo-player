class MopidyRFIDError(Exception):
    pass


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

    if device == "rc522":
        from mopidy_rfid.devices.rc522 import RC522Device

        return RC522Device(config)

    raise NotImplementedError("Device {} not known".format(device))
