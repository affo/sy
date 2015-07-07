import unittest
from sy.sensors.base import BaseSensor
from sy.exceptions import SensorError

class DummySensor(BaseSensor):
    index = 0

    def _get(self):
        i = self.index
        self.index += 1
        return i


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

