import ConfigParser as cp

CONFIG_FILE = 'sy.conf'

def _to_str():
    return lambda o: str(o)

def _to_int():
    return lambda o: int(o)

def _to_float():
    return lambda o: float(o)

def _to_list():
    def fn(o):
        return o.split(',')
    return fn

OPTS = {
    # option_name: (default_value, cast_function)
    'sy_host': ('localhost', _to_str),
    'sy_port': ('5000', _to_int),
    'rabbit_host': ('localhost', _to_str),
    'rabbit_port': ('5672', _to_int),
    'redis_host': ('localhost', _to_str),
    'redis_port': ('6379', _to_int),
    'docker_url': ('unix://var/run/docker.sock', _to_str),
}

CONF = cp.ConfigParser(defaults={k: v[0] for k, v in OPTS.items()})
CONF.readfp(open(CONFIG_FILE))

def get(option, section='DEFAULT'):
    value = CONF.get(section, option)
    cast_fn = OPTS[option][1]()
    return cast_fn(value)
