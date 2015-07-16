from gevent import monkey
monkey.patch_all()
from sy.tests.integration.base import RMQTestCase
from sy.sensors.usage import CPUMemoryPercSensor
from sy.api import RMQConsumer

class TestCPUMemUsage(RMQTestCase):
    def onRabbitUp(self):
        self.rmq = RMQConsumer()

    def test_cpu_mem_are_percentages(self):
        cid = self._start_test_container(time=100)
        s = CPUMemoryPercSensor({'cid': cid})
        s.start()

        _, _, top = next(self.rmq.consume())

        vals = top['tot'].values()
        del top['tot']
        for p in top.values():
            usages = p['usage'].values()
            vals.extend(usages)

        for v in vals:
            self.assertTrue(v >= 0 and v <= 100)

        s.kill()

    def test_tot_is_reasonable(self):
        cid = self._start_test_container(time=100)
        s = CPUMemoryPercSensor({'cid': cid})
        s.start()

        _, _, top = next(self.rmq.consume())

        real_tot = top['tot']
        del top['tot']

        expected_tot = {k: 0 for k in real_tot.keys()}
        for p in top.values():
            for k, v in p['usage'].items():
                expected_tot[k] += v

        self.assertEqual(real_tot, expected_tot)

        s.kill()
