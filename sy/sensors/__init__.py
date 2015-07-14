from sy.tests import dummy

TYPES = {
    'dummy': dummy.DummySensor,
    'dummy_redis': dummy.DummyRedisSensor,
    'dummy_rmq': dummy.DummyRMQSensor,
}
