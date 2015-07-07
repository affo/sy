Integration testing is performed launching RabbitMQ and Redis in Docker containers (`test-rabbit` and `test-redis` respectively).  
Module `sy.tests.integration` offers `setup_package` and `teardown_package`, package-level fixtures to automate containers start and removal.  
Module `sy.tests.integration.base` offers `RMQTestCase` and `RedisTestCase` classes. Extend those classes in your integration test cases.  
At each test method, the `setUp` method will clear all RabbitMQ queues and messages and flush Redis data.  
If you want to add custom behavior on test case setup override `onRabbitUp` or `onRedisUp` called as hooks at the end of `setUp`. In the case of `tearDown` override `onRabbitDown` and `onRedisDown`.

## Example
File `sy/tests/integration/test_foo.py`:

```python
from sy.tests.integration.base import RMQTestCase

class FooTestCase(RMQTestCase):
    def onRabbitUp(self):
        # my awesome setup
        pass

    def onRabbitUp(self):
        # my awesome tear down
        pass

    def test_foo(self):
        # test code that interacts
        # with RabbitMQ
        self.assertTrue(True)
```

Run with [Nose](https://nose.readthedocs.org/en/latest/).
