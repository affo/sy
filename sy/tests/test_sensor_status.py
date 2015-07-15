from unittest import TestCase
from sy.daemon import SensorsStatus
from sy import exceptions as syex

class SensorStatusTestCase(TestCase):
    def setUp(self):
        self.status = SensorsStatus()

    def test_add_adds(self):
        uid = self.status.add('foo_cid', 'dummy')
        sensors = self.status.sensors.keys()
        self.assertEqual(len(sensors), 1)
        sensor = sensors[0]
        self.assertEqual(sensor, uid)

    def test_add_same_sensor_does_not_change(self):
        uid = self.status.add('foo_cid', 'dummy')
        uid = self.status.add('foo_cid', 'dummy')
        sensors = self.status.sensors.keys()
        self.assertEqual(len(sensors), 1)
        sensor = sensors[0]
        self.assertEqual(sensor, uid)

    def test_add_invalid_sensor_type(self):
        with self.assertRaises(syex.InvalidSensorType):
            uid = self.status.add('foo_cid', 'invalid_sensor_type')

    def test_remove_removes(self):
        uid = self.status.add('foo_cid', 'dummy')
        self.status.remove('foo_cid', 'dummy')
        self.assertEqual(len(self.status.sensors), 0)

    def test_remove_invalid_sensor_type(self):
        with self.assertRaises(syex.InvalidSensorType):
            self.status.remove('foo_cid', 'invalid_sensor_type')

    def test_remove_non_existent_sensor(self):
        with self.assertRaises(syex.NoSensorFound):
            self.status.remove('not_found', 'dummy')
