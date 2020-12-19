# Installation

Logging into a freshly set up Raspberry Pi, this should install *everything*:

```
sudo apt install git python3-pip
python3 -m pip install git+https://github.com/dokempf/cookiecutter.git@vyvo-merge
cookiecutter gh:dokempf/vyvo-player
./installer/install.sh
```
