import os

# Remove the configured versions of the hooks/Jinja extensions
os.remove("pre_gen_project.py")
os.remove("post_gen_project.py")
os.remove("__init__.py")

# Remove some unneeded files:
if "{{ cookiecutter.power_switch }}" != "Simple":
    os.remove("gpio_if.sh")
    os.remove("powerswitch-sync.service")
