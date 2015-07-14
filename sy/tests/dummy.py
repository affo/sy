from sy.sensors import base
from datetime import datetime

class DummySensor(base.BaseSensor):
    index = 0

    def _get(self):
        i = self.index
        self.index += 1
        return i


class DummyRMQSensor(base.BaseRMQSensor):
    index = 0

    def _get(self):
        i = self.index
        self.index += 1
        return i


class DummyRedisSensor(base.BaseRedisSensor):
    def _get(self):
        return {
            'dummy': 'data',
            'ts': str(datetime.now())
        }
