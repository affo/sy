class Error(Exception):
    """Base class"""
    pass


class SensorError(Error):
    """Error raised by a sensor"""
    pass

#### daemon's exceptions
class DaemonError(Error):
    def __init__(self, *args, **kwargs):
        Error.__init__(self)
        self.error_dict = kwargs

    def to_dict(self):
        errors = self.error_dict.copy()
        errors.update({'message': self.message})
        return errors


class InvalidSensorType(DaemonError):
    def __init__(self, invalid_stype, **kwargs):
        DaemonError.__init__(self, **kwargs)
        self.message = '{} is not an allowed sensor type'.format(invalid_stype)


class NoSensorFound(DaemonError):
    def __init__(self, cid, stype, **kwargs):
        DaemonError.__init__(self, **kwargs)
        self.message = 'No sensor found with type {} and id {}.'.format(stype, cid)


class BadJsonInput(DaemonError):
    def __init__(self, *wrong_keys, **kwargs):
        DaemonError.__init__(self, **kwargs)
        self.message = 'Not allowed key(s) found.'
        self.error_dict['wrong_keys'] = wrong_keys
