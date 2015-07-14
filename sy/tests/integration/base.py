import unittest
from sy.tests.integration import refresh_rabbit, refresh_redis

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
