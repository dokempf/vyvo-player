import re
from setuptools import find_packages, setup


def get_version(filename):
    content = open(filename).read()
    return re.search('__version__ = "([^"]+)"', content).group(1)


setup(
    name="Mopidy-rfid",
    version=get_version("mopidy_rfid/__init__.py"),
    author="Dominic Kempf",
    author_email="dominic.r.kempf@gmail.com",
    packages=find_packages(),
    entry_points={"mopidy.ext": ["rfid = mopidy_rfid:Extension",],},
)
