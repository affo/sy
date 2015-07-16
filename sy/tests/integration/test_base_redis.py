from gevent import monkey
monkey.patch_all()
from sy.tests.integration.base import RedisTestCase
from sy.tests.dummy import DummyRedisSensor
from sy.api import RedisAPI

class BaseRedisTestCase(RedisTestCase):
    def onRedisUp(self):
        self.cid = 'non-existent-container'
        self.redis = RedisAPI()
        self.s = DummyRedisSensor({'cid': self.cid})
        self.s.start()

    def onRedisDown(self):
        self.s.kill()

    def test_values(self):
        expected = next(self.s.get_data())

        real = self.redis.get(self.s.uid)
        self.assertEqual(expected, real)
