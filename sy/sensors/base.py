from gevent import sleep, Greenlet
from gevent.coros import BoundedSemaphore
from sy import config, log, api
from sy.exceptions import SensorError
import json

LOG = log.get(__name__)

def get_uid(sensor_class, cid):
    return '_'.join([cid, sensor_class.__name__.lower()])

class BaseSensor(Greenlet):
    """
    Base class for sensors.  
    Each sensor is associated with a Docker container by its 
    cid (or name, if you prefer).  
    A sensor has to be started with its `start` method, eventually, 
    stopped with its `kill` method.

    Every sensor provides collected data by means of 
    `get_data` method which returns a generator.
    Each call to `next` value is blocking for a time declared 
    on `__init__` of the sensor through `spacing` parameter.
    """
    def __init__(self, cid, spacing=0.1):
        Greenlet.__init__(self)
        self.cid = cid
        self.uid = get_uid(self.__class__, cid)
        self.spacing = spacing
        self._lock = BoundedSemaphore()
        self._lock.acquire() # locking semaphore
        self._new_data = None

    def _run(self):
        while True:
            self._new_data = self._get()
            LOG.debug("{} got {}".format(self.__class__.__name__, self._new_data))
            self._store(self._new_data)
            self._lock.release()
            sleep(self.spacing)


    def _get(self):
        """Override"""
        return None

    def _store(self, data):
        """Override"""
        pass

    def get_data(self):
        while True:
            if not self.started or self.dead:
                raise SensorError("Start the sensor before getting data.")
            self._lock.acquire()
            yield self._new_data


class BaseRMQSensor(BaseSensor):
    def __init__(self, cid, **kwargs):
        super(BaseRMQSensor, self).__init__(cid, **kwargs)
        # getting values from config
        rabbit_host = config.get('rabbit_host')
        rabbit_port = config.get('rabbit_port')
        self.rmqapi = api.RMQPublisher(
            rabbit_host=rabbit_host,
            rabbit_port=rabbit_port
        )

    def _store(self, data):
        self.rmqapi.publish(data)


class BaseRedisSensor(BaseSensor):
    def __init__(self, cid, **kwargs):
        super(BaseRedisSensor, self).__init__(cid, **kwargs)
        # getting values from config
        redis_host = config.get('redis_host')
        redis_port = config.get('redis_port')
        self.redisapi = api.RedisAPI(redis_host, redis_port)

    def _store(self, data):
        # TODO use return value?
        self.redisapi.set(self.cid, data)
