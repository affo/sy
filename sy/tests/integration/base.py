import unittest
from sy.sensors.base import BaseRMQSensor, BaseRedisSensor
from sy.tests.integration import refresh_rabbit, refresh_redis

class DummyRMQSensor(BaseRMQSensor):
    index = 0

    def _get(self):
        i = self.index
        self.index += 1
        return i


class DummyRedisSensor(BaseRedisSensor):
    def _get(self):
        return {
            'i': 'am',
            'dummy': 'data',
        }


class RMQTestCase(unittest.TestCase):
    def setUp(self):
        refresh_rabbit()
        # call implementors setUp
        self.onRabbitUp()

    def tearDown(self):
        # call implementors tearDown
        self.onRabbitDown()

    def onRabbitUp(self):
        pass

    def onRabbitDown(self):
        pass


class RedisTestCase(unittest.TestCase):
    def setUp(self):
        refresh_redis()
        # call implementors setUp
        self.onRedisUp()

    def tearDown(self):
        # call implementors tearDown
        self.onRedisDown()

    def onRedisUp(self):
        pass

    def onRedisDown(self):
        pass
