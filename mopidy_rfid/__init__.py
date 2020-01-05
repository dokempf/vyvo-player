import os
from mopidy import config, ext

from mopidy_rfid.apps import app_factory
from mopidy_rfid.command import DispatchCommand
from mopidy_rfid.frontend import RFIDFrontend

# This is the unique location of this version string throughout the code
__version__ = "0.1"


class Extension(ext.Extension):
    dist_name = "Mopidy-rfid"
    ext_name = "rfid"
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), "ext.conf")
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema["device"] = config.String(choices=["diskmock", "rc522"])
        return schema

    def get_command(self):
        return DispatchCommand()

    def setup(self, registry):
        registry.add("frontend", RFIDFrontend)

        registry.add("http:app", {"name": self.ext_name, "factory": app_factory})
