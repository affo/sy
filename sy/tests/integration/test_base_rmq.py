from gevent import monkey
monkey.patch_all()
from sy.tests.integration.base import RMQTestCase
from sy.tests.dummy import DummyRMQSensor
from sy.api import RMQConsumer

class BaseRMQTestCase(RMQTestCase):
    def onRabbitUp(self):
        self.rmq = RMQConsumer()
        self.s = DummyRMQSensor({'cid': 'non-existent-container'})
        self.s.start()

    def onRabbitDown(self):
        self.s.kill()

    def test_values(self):
        n_msg = 10
        # push results to rabbit
        expected = []
        for i, d in enumerate(self.s.get_data()):
            expected.append(d)
            if i == n_msg - 1:
                break

        # get messages from rabbit
        real = [body for _, _, body in self.rmq.consume(n_msg)]
        self.assertEqual(expected, real)
