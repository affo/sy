from sy.tests.integration.base import RedisTestCase, DummyRedisSensor
from sy.sensors.base import BaseRedisSensor
from sy.api import RedisAPI

class BaseRedisTestCase(RedisTestCase):
    def onRedisUp(self):
        self.cid = 'non-existent-container'
        self.redis = RedisAPI()
        self.s = DummyRedisSensor(self.cid)
        self.s.start()

    def onRedisDown(self):
        self.s.kill()

    def test_values(self):
        expected = next(self.s.get_data())

        real = self.redis.get(self.cid)
        self.assertEqual(expected, real)
