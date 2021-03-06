import re
from setuptools import find_packages, setup


def get_version(filename):
    content = open(filename).read()
    return re.search('__version__ = "([^"]+)"', content).group(1)


setup(
    name="Vyvo-Player",
    version=get_version("vyvo/__init__.py"),
    author="Dominic Kempf",
    author_email="dominic.r.kempf@gmail.com",
    packages=find_packages(),
    entry_points={"mopidy.ext": ["vyvo = vyvo:Extension"]},
    install_requires=[
        "Mopidy >= 3.0",
        "Pykka",
        "tornado",
        "pi-rc522",
        "pytimeparse",
    ],
)
