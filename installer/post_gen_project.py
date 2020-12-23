import os

# Remove the configured versions of the hooks/Jinja extensions
os.remove("pre_gen_project.py")
os.remove("post_gen_project.py")
os.remove("__init__.py")

# Cut the install.sh script into chunks at reboot
index = 0

def newscript():
    global index
    f = open("install-{}.sh".format(index), "w")
    os.chmod("install-{}.sh".format(index), 0o755)
    f.write("#!/bin/bash\n")
    f.write("set -e\n")
    index = index + 1
    return f

current = newscript()
for line in open("install.sh", "r"):
    if line.startswith("reboot"):
        restart_command = "sudo ./installer/install-{}.sh".format(index)
        current.write("\n# Preparing a reboot + continue\n")
        current.write("echo '{}' >> ~/.bashrc\n".format(restart_command))
        current.write("reboot\n")
        current.close()
        current = newscript()
        current.write('sed -i "s/{}//g" ~/.bashrc'.format(restart_command))
    else:
        current.write(line)
current.close()

# Now write the "real" install script
with open("install.sh", "w") as f:
    f.write("#!/bin/bash\n")
    f.write("./installer/install-0.sh")
