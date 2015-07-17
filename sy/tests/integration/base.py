import unittest
from sy.tests.integration import refresh_rabbit, refresh_redis, start_busybox, remove_container

class LaunchTestContainersTestCase(unittest.TestCase):
    def _start_test_container(self, name='test', time=10):
        cid = start_busybox(name, time)
        self.test_containers.append(cid)
        return cid

    def setUp(self):
        self.test_containers = []

    def tearDown(self):
        for tc in self.test_containers:
            remove_container(tc)


class RMQTestCase(LaunchTestContainersTestCase):
    def setUp(self):
        super(RMQTestCase, self).setUp()
        refresh_rabbit()
        # call implementors setUp
        self.onRabbitUp()

    def tearDown(self):
        # call implementors tearDown
        self.onRabbitDown()
        super(RMQTestCase, self).tearDown()

    def onRabbitUp(self):
        pass

    def onRabbitDown(self):
        pass


class RedisTestCase(LaunchTestContainersTestCase):
    def setUp(self):
        super(RedisTestCase, self).setUp()
        refresh_redis()
        # call implementors setUp
        self.onRedisUp()

    def tearDown(self):
        super(RedisTestCase, self).tearDown()
        # call implementors tearDown
        self.onRedisDown()

    def onRedisUp(self):
        pass

    def onRedisDown(self):
        pass
