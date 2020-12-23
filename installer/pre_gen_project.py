import re
import sys


if not re.match("^[a-zA-Z][a-zA-Z0-9]*$", "{{ cookiecutter.hostname }}"):
    sys.stderr.write("Illegal hostname. Hostnames should consists of letters and numbers only.")
    sys.exit(1)
