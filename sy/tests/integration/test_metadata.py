from gevent import monkey
monkey.patch_all()
from sy.tests.integration.base import RedisTestCase
from sy.sensors import metadata
from sy.api import RedisAPI, DockerAPI

class MetadataSensorsTest(RedisTestCase):
    def onRedisUp(self):
        self.redis = RedisAPI()
        self.cid = self.test_container_name = 'test_meta'
        self.docker = DockerAPI(self.test_container_name)
        self._start_test_container(name=self.test_container_name)
        self.alls = metadata.AllMetadataSensor({'cid': self.test_container_name, 'spacing': 3})
        self.ips = metadata.IPSensor({'cid': self.test_container_name, 'spacing': 3})
        self.hcs = metadata.HostConfigSensor({'cid': self.test_container_name, 'spacing': 3})

        self.alls.start()
        self.ips.start()
        self.hcs.start()

    def onRedisDown(self):
        self.alls.kill()
        self.ips.kill()
        self.hcs.kill()

    def test_values(self):
        expected = self.docker.inspect()

        real = self.redis.get(self.alls.uid)
        self.assertEqual(expected, real)

        real = self.redis.get(self.ips.uid)
        self.assertEqual(expected['NetworkSettings']['IPAddress'], real['IPAddress'])

        real = self.redis.get(self.hcs.uid)
        self.assertEqual(expected['HostConfig'], real['HostConfig'])
