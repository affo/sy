from pika.exceptions import AMQPConnectionError as RMQConnError
from redis.exceptions import ConnectionError as RedisConnError
from requests.exceptions import ConnectionError as DockerConnError
from functools import wraps

class Error(Exception):
    """Base class"""
    pass


class SensorError(Error):
    """Error raised by a sensor"""
    pass


class ServiceConnectionError(SensorError):
    """Errors raised in sensors for connection errors with services"""
    pass

def raise_connection_error(fn):
    """
    Wrapper that raises any connection error from the services we
    depend on (RabbitMQ, Redis, Docker) as a single connection error.
    Use it only to wrap methods. Supposing that the first arg is self.
    """
    @wraps(fn)
    def wrap_error(*args, **kwargs):
        message = None
        try:
            fn(*args, **kwargs)
        except DockerConnError:
            message = "{}: Docker service not found.".format(args[0].__class__.__name__)
        except RMQConnError:
            message = "{}: RabbitMQ service not found.".format(args[0].__class__.__name__)
        except RedisConnError:
            message = "{}: Redis service not found.".format(args[0].__class__.__name__)
        finally:
            if message is not None:
                raise ServiceConnectionError(message)
    return wrap_error


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
