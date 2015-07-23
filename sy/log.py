import logging, subprocess

_loggers = {}


class CustomFilter(logging.Filter):
    def filter(self, record):
        root_module = record.name.split('.')[0]
        return root_module == 'sy' or record.levelno > logging.DEBUG


class ColoredFormatter(logging.Formatter):
    RESET = '\e[0m'
    RED = '\e[0;31m'
    GREEN = '\e[0;32m'
    YELLOW = '\e[0;33m'
    BLUE = '\e[0;34m'
    PURPLE = '\e[0;35m'
    CYAN = '\e[0;36m'
    WHITE = '\e[0;37m'

    def __init__(self, *args, **kwargs):
        super(ColoredFormatter, self).__init__(*args, **kwargs)
        try:
            self.RESET = subprocess.check_output('tput sgr0'.split())
            self.RED = subprocess.check_output('tput setaf 1'.split())
            self.GREEN = subprocess.check_output('tput setaf 2'.split())
            self.YELLOW = subprocess.check_output('tput setaf 3'.split())
            self.BLUE = subprocess.check_output('tput setaf 4'.split())
            self.MAGENTA = subprocess.check_output('tput setaf 5'.split())
            self.CYAN = subprocess.check_output('tput setaf 6'.split())
            self.WHITE = subprocess.check_output('tput setaf 7'.split())
        except subprocess.CalledProcessError:
            self.RESET = self.RED = self.GREEN = self.YELLOW = ''
            self.BLUE = self.MAGENTA = self.CYAN = slef.WHITE = ''

        self.LEVEL_COLORS = {
            'DEBUG': self.GREEN,
            'INFO': self.CYAN,
            'WARNING': self.YELLOW,
            'ERROR': self.RED,
            'CRITICAL': self.RED
        }

    def format(self, record):
        msg = super(ColoredFormatter, self).format(record)
        lvl = record.levelname
        return ''.join([self.LEVEL_COLORS[lvl], msg, self.RESET])


def _new_logger(name):
    l = logging.getLogger(name)
    l.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    fh = logging.FileHandler(filename='sy.log')

    ff = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s]: %(message)s')
    sf = ColoredFormatter('%(asctime)s: %(message)s', datefmt='%H:%M:%S')

    filt = CustomFilter()
    sh.addFilter(filt)
    fh.addFilter(filt)
    sh.setFormatter(sf)
    fh.setFormatter(ff)
    sh.setLevel(logging.INFO)
    fh.setLevel(logging.DEBUG)

    l.addHandler(sh)
    l.addHandler(fh)

    return l

def get(module_name):
    global _loggers

    logger = _loggers.get(module_name, None)
    if logger is None:
        logger = _new_logger(module_name)
        _loggers[module_name] = logger
    return logger
