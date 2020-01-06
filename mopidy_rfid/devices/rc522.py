from mopidy_rfid.devices import RFIDDeviceBase, MopidyRFIDError

from pirc522 import RFID


def mifare1k_block_address_generator():
    for sector in range(16):
        for block in range(3):
            if not ((sector == 0) and (block in (0, 1))):
                yield sector * 4 + block


def err_handle(ret):
    if isinstance(ret, tuple):
        if ret[0]:
            raise MopidyRFIDError("Encountered error in handling of RFID tag")
        if len(ret) == 2:
            # Unpacking 1-tuples for better readability
            return ret[1]
        else:
            return ret[1:]
    else:
        return None


class RC522Device(RFIDDeviceBase):
    def __init__(self, config):
        self.reader = RFID()

    def read(self):
        # Send a request to the RFID Reader
        self.reader.init()
        error, tag_type = self.reader.request()

        # If we did not encounter a tag, do nothing
        if tag_type is None:
            return None

        if error:
            raise MopidyRFIDError("Found RFID tag, but still produced an error")

        uid = err_handle(self.reader.anticoll())
        err_handle(self.reader.select_tag(uid))

        def read_block(address):
            err_handle(
                self.reader.card_auth(
                    self.reader.auth_a,
                    address,
                    [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF],
                    uid,
                )
            )
            return err_handle(self.reader.read(address))

        # Read the number of bytes from special block (address 1)
        size = int.from_bytes(read_block(1), byteorder="little")

        # Read all data blocks from the card
        data = []
        for i, addr in zip(range(0, size, 16), mifare1k_block_address_generator()):
            data.extend(read_block(addr))

        # Truncate padding from the data blocks
        data = data[:size]

        # Recover string from the raw bytes
        return str(bytes(data), encoding="utf-8")

    def write(self, uri):
        self.reader.init()
        tag_type = err_handle(self.reader.request())

        # If we did not encounter a tag, do nothing
        if tag_type is None:
            print("Tried writing, but no RFID card found (warning)")
            return None

        uid = err_handle(self.reader.anticoll())
        err_handle(self.reader.select_tag(uid))

        def write_block(address, block_data):
            err_handle(
                self.reader.card_auth(
                    self.reader.auth_a,
                    address,
                    [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF],
                    uid,
                )
            )
            return err_handle(self.reader.write(address, block_data))

        data = bytes(uri, encoding="utf-8")
        size = len(data)

        # Pad data to a multiple of 16
        data = b"".join([data] + [b"0"] * (16 - size % 16))

        # Write all data blocks to the card
        write_block(1, size.to_bytes(16, byteorder="little"))
        for i, addr in zip(range(0, size, 16), mifare1k_block_address_generator()):
            write_block(addr, data[i : i + 16])
