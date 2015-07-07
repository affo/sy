import logging

logging.basicConfig(filename='sy.log', level=logging.DEBUG)

_loggers = {}

def get(module_name):
    global _loggers

    logger = _loggers.get(module_name, None)
    if logger is None:
        logger = logging.getLogger(module_name)
        _loggers[module_name] = logger
    return logger
