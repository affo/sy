import json, pika, redis
from sy import log

EXCHANGE_NAME = 'monitor'
KEY_TOPIC = 'sensors'
LOG = log.get(__name__)

_connection = None

class RMQBase(object):
    def __init__(self, rabbit_host='localhost', rabbit_port=5672):
        global _connection
        super(RMQBase, self).__init__()

        if _connection is None:
            _connection = pika.BlockingConnection(
                pika.ConnectionParameters(rabbit_host, rabbit_port)
            )

        self._channel = _connection.channel()
        self._channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            type='topic'
        )


class RMQPublisher(RMQBase):
    def __init__(self, *args, **kwargs):
        super(RMQPublisher, self).__init__(*args, **kwargs)
        routing_key = [KEY_TOPIC, self.__class__.__name__.lower()]
        self.routing_key='.'.join(routing_key)

    def publish(self, data):
        self._channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=self.routing_key,
            body=json.dumps(data)
        )
        LOG.debug("On {} sent:{}".format(self.routing_key, data))


class RMQConsumer(RMQBase):
    def __init__(self, topic='*', *args, **kwargs):
        super(RMQConsumer, self).__init__(*args, **kwargs)
        q = self._channel.queue_declare(exclusive=True)
        self._q_name = q.method.queue
        self._channel.queue_bind(
            exchange=EXCHANGE_NAME,
            queue=self._q_name,
            routing_key='.'.join([KEY_TOPIC, topic])
        )

    def consume(self, n_msg=0):
        try:
            # n_msg = 0 means infinite
            for method, properties, body in self._channel.consume(self._q_name):
                LOG.info('On {} got: {}'.format(method.routing_key, body))
                self._channel.basic_ack(method.delivery_tag)
                yield method, properties, json.loads(body)

                if n_msg != 0 and method.delivery_tag == n_msg:
                    break
        except KeyboardInterrupt:
            self._connection.close()


class RedisAPI(object):
    def __init__(self, redis_host='localhost', redis_port=6379):
        super(RedisAPI, self).__init__()
        self.cli = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

    def get(self, cid):
        value = self.cli.get(cid)
        if value is not None:
            value = json.loads(value)
        return value

    def set(self, cid, data):
        data = json.dumps(data)
        res = self.cli.set(cid, data)
        LOG.debug('{{ {} : {} }} stored.'.format(cid, data))
        return res
