import os
from mopidy import config, ext


# This is the unique location of this version string throughout the code
__version__ = "0.1"


class Extension(ext.Extension):
    dist_name = "Vyvo-Player"
    ext_name = "vyvo"
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), "ext.conf")
        return config.read(conf_file)

    def get_config_schema(self):
        from vyvo.schema import Timedelta

        schema = super(Extension, self).get_config_schema()
        schema["device"] = config.String(choices=["diskmock", "rc522"])
        schema["polling_interval"] = config.Integer(minimum=100)
        schema["antenna_gain"] = config.Integer(minimum=0, maximum=7)
        schema["resume_threshold"] = Timedelta()
        return schema

    def get_command(self):
        from vyvo.command import DispatchCommand

        return DispatchCommand()

    def setup(self, registry):
        from vyvo.frontend import RFIDFrontend

        registry.add("frontend", RFIDFrontend)

        # Deliver the web client
        registry.add('http:static', {
            'name': self.ext_name,
            'path': os.path.join(os.path.dirname(__file__), '..', 'app'),
        })

        # Add the API
        from vyvo.api import api_factory
        registry.add("http:app", {
            "name": self.ext_name + "_api",
            "factory": api_factory
        })
