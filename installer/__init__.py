from cookiecutter.utils import simple_filter


@simple_filter
def hostname(v):
    """ Make this string the hostname. This is a filter because I am too lazy to research what other Jinja2 construct might do the job """
    with open("/etc/hostname") as f:
        return f.readline().strip()

