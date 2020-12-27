import pykka
from vyvo import logger


class MopidyDeviceError(Exception):
    pass


class RFIDDeviceBase:
    def minimum_flakiness(self):
        """ Returns the flakiness characteristics of the device.
        This is a tuple of integers (n, m). The device actor will
        always trigger n operations m of which need to agree on the
        result.
        """
        return 1, 1

    def read(self):
        raise NotImplementedError

    def write(self, uri):
        raise NotImplementedError


class DeviceActor(pykka.ThreadingActor):
    """ This actor manages access to the physical device. By only using the
    device through this actor, it is guaranteed that there is no conflict at
    the device level, although different parts of the project access the device.
    """
    def __init__(self, config):
        super(DeviceActor, self).__init__()
        self.device = None

        if config["vyvo"]["device"] == "diskmock":
            from vyvo.devices.diskmock import DiskMockDevice
            self.device = DiskMockDevice(config)

        if config["vyvo"]["device"] == "rc522":
            from vyvo.devices.rc522 import RC522Device
            self.device = RC522Device(config)

        if self.device is None:
            raise NotImplementedError("Device {} not known".format(config["vyvo"]["device"]))

        # Parse flakiness from the given configuration and from the device settings
        # and use the maximum of these.
        config_flakiness = config["vyvo"]["device_flakiness"]
        min_flakiness = self.device.minimum_flakiness()
        self.flakiness = tuple(max(int(config_flakiness[i]), min_flakiness[i]) for i in range(2))

    def on_receive(self, message):
        if message == "read":
            results = {}
            for i in range(self.flakiness[0]):
                try:
                    uri = self.device.read()
                    results[uri] = results.setdefault(uri, 0) + 1
                except MopidyDeviceError as e:
                    results[e] = results.setdefault(e, 0) + 1

            # Determine the result that dominated the sequence of reads
            best = max(results, key=lambda k: results[k])

            # Log a disagreement in results
            if results[best] != self.flakiness[0] or isinstance(best, MopidyDeviceError):
                print(results)
                logger.info("Device flakiness report: Agreement was {}/{} attempts".format(results[best], self.flakiness[0]))

            if results[best] < self.flakiness[1]:
                logger.info("Device flakiness report: Treating as if no tag was found")
                return None

            if isinstance(best, MopidyDeviceError):
                raise best

            return best
        elif message.startswith("write:"):
            # Try n times
            for i in range(self.flakiness[0]):
                try:
                    return self.device.write(message[6:])
                except MopidyDeviceError:
                    pass
            raise MopidyDeviceError
        else:
            raise ValueError("DeviceActor expects 'read' or 'write:<uri>' as message!")
