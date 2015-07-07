import ConfigParser as cp

CONFIG_FILE = 'sy.conf'

def _to_str():
    return lambda o: str(o)

def _to_int():
    return lambda o: int(o)

def _to_list():
    def fn(o):
        return o.split(',')
    return fn

OPTS = {
    # option_name: (default_value, cast_function)
    'rabbit_host': ('localhost', _to_str),
    'rabbit_port': ('5672', _to_int),
    'redis_host': ('localhost', _to_str),
    'redis_port': ('6379', _to_int),
}

config = cp.ConfigParser(defaults={k: v[0] for k, v in OPTS.items()})
config.readfp(open(CONFIG_FILE))

def get(option, section='DEFAULT'):
    value = config.get(section, option)
    cast_fn = OPTS[option][1]()
    return cast_fn(value)
