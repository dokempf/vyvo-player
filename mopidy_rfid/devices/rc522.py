from mopidy_rfid.devices import RFIDDeviceBase, MopidyRFIDError

from pirc522 import RFID


def err_handle(*ret):
    if ret[0]:
        raise MopidyRFIDError("Encountered error in handling of RFID tag")
    if len(ret) == 2:
        # Unpacking 1-tuples for better readability
        return ret[1]
    else:
        return ret[1:]


class RC522Device(RFIDDeviceBase):
    def __init__(self, config):
        self.reader = RFID()
        self.util = self.reader.util()

    def read(self):
        # Send a request to the RFID Reader
        tag_type = err_handle(self.reader.request())

        # If we did not encounter a tag, do nothing
        if tag_type is None:
            return None

        uid = err_handle(self.reader.anticoll())
        err_handle(self.reader.select_tag(uid))

        print("Detected an RFID card with UID={}".format(uid))

        # Lines from example not adapted yet

    #         self.util.auth(self.reader.auth_b, [0x74, 0x00, 0x52, 0x35, 0x00, 0xFF])
    #         self.util.read_out(4)
    #         self.util.deauth()

    def write(self, uri):
        pass
