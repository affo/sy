from gevent import monkey
monkey.patch_all()
from unittest import TestCase
from sy.daemon import SensorsStatus
from sy import exceptions as syex

class SensorStatusTestCase(TestCase):
    def setUp(self):
        self.status = SensorsStatus()

    def test_add_adds(self):
        sensor, warn = self.status.add({'cid': 'foo_cid'}, 'dummy')
        sensors = self.status.sensors
        self.assertEqual(len(sensors), 1)
        self.assertEqual(sensor.to_primitive(), sensors[sensor.uid].to_primitive())
        self.assertEqual(warn, '')

    def test_add_same_sensor_does_not_change(self):
        sensor, _ = self.status.add({'cid': 'foo_cid', 'spacing': 42}, 'dummy')
        _, warn = self.status.add({'cid': 'foo_cid', 'spacing': 43}, 'dummy')
        sensors = self.status.sensors
        self.assertEqual(len(sensors), 1)
        self.assertEqual(sensor.to_primitive(), sensors[sensor.uid].to_primitive())
        self.assertTrue(warn)

    def test_remove_removes(self):
        self.status.add({'cid': 'foo_cid'}, 'dummy')
        self.status.remove('foo_cid', 'dummy')
        self.assertEqual(len(self.status.sensors), 0)

    def test_remove_non_existent_sensor(self):
        with self.assertRaises(syex.NoSensorFound):
            self.status.remove('not_found', 'dummy')
