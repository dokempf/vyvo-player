from mopidy_rfid.devices import RFIDDeviceBase

import os


class DiskMockDevice(RFIDDeviceBase):
    def __init__(self, config):
        cache_dir = config["core"]["cache_dir"]
        self.diskfile = os.path.join(cache_dir, "diskmock.file")

    def read(self):
        try:
            return open(self.diskfile).read()
        except FileNotFoundError:
            return None

    def write(self, uri):
        if uri in ("None", ""):
            return os.remove(self.diskfile)

        return open(self.diskfile, "w").write(uri)
