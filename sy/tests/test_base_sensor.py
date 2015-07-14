import unittest
from sy.exceptions import SensorError
from sy.tests.dummy import DummySensor

class BaseSensorTest(unittest.TestCase):

    def setUp(self):
        self.s = DummySensor('non-existent-container')

    def tearDown(self):
        self.s.kill()

    def _start_sensor(self):
        self.s.start()

    def test_new_data_generator(self):
        self._start_sensor()
        for i, d in enumerate(self.s.get_data()):
            self.assertEquals(d, i)
            if i == 5:
                break

    def test_stopped_sensor_raises_exception(self):
        with self.assertRaises(SensorError):
            next(self.s.get_data())

