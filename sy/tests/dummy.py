from sy.sensors import base

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
            'i': 'am',
            'dummy': 'data',
        }
