from docker import Client
from docker.utils import create_host_config
from sy import config, log
import time, pika
import pika.exceptions

LOG = log.get(__name__)
docker_client = Client(base_url='unix://var/run/docker.sock')
RMQ_CID = None
REDIS_CID = None

def wait_for_rabbit():
    timeout = 30
    count = 0
    while count < timeout:
        try:
            # Supposing tests to run on localhost
            pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            return
        except pika.exceptions.IncompatibleProtocolError:
            LOG.debug('Waiting for rabbitmq container to be up')
            time.sleep(1)
            count += 1
    else:
        raise Exception('Too much time passed waiting on Rabbit to be up. Check your Docker configuration')

def start_rabbit():
    # launch a rabbitmq container and bind it to port given by config:
    # docker run -d -e RABBITMQ_NODENAME=test-rabbit --name test-rabbit -p <rabbit_port>:5672 rabbitmq:3
    # first, ensure that we have the image
    docker_client.pull('rabbitmq', tag='3')
    # then create the container
    rabbit_port = config.get('rabbit_port')
    cid = docker_client.create_container(
        image='rabbitmq:3',
        detach=True,
        environment={'RABBITMQ_NODENAME': 'test-rabbit'},
        name='test-rabbit',
        ports=[rabbit_port],
        host_config=create_host_config(port_bindings={
            rabbit_port: 5672
        })
    )['Id']
    # now we can start it
    docker_client.start(cid)
    wait_for_rabbit()
    return cid

def refresh_rabbit():
    global RMQ_CID
    assert RMQ_CID is not None, "No RabbitMQ container found."

    eid = docker_client.exec_create(RMQ_CID, 'rabbitmqctl reset')['Id']
    docker_client.exec_start(eid)

def start_redis():
    # launch a redis container and bind it to port given by config:
    # docker run -d --name test-redis -p <redis_port>:6379 redis
    # first, ensure that we have the image
    docker_client.pull('redis', tag='latest')
    # then create the container
    redis_port = config.get('redis_port')
    cid = docker_client.create_container(
        image='redis:latest',
        detach=True,
        name='test-redis',
        ports=[redis_port],
        host_config=create_host_config(port_bindings={
            redis_port: 6379
        })
    )['Id']
    # now we can start it
    docker_client.start(cid)
    return cid

def refresh_redis():
    global REDIS_CID
    assert REDIS_CID is not None, "No Redis container found."

    eid = docker_client.exec_create(REDIS_CID, 'redis-cli flushall')['Id']
    docker_client.exec_start(eid)

def start_busybox(sleep_time=3):
    docker_client.pull('busybox', tag='latest')
    # then create the container
    cid = docker_client.create_container(
        image='busybox:latest',
        command='sleep ' + str(sleep_time),
        detach=True,
    )['Id']
    # now we can start it
    docker_client.start(cid)
    return cid

def remove_container(cid):
    docker_client.remove_container(
        container=cid,
        force=True
    )

#### package level fixtures

def setup_package():
    global RMQ_CID, REDIS_CID
    assert RMQ_CID is None, "RabbitMQ is up. Remove it first."
    assert REDIS_CID is None, "Redis is up. Remove it first."

    RMQ_CID = start_rabbit()
    REDIS_CID = start_redis()

def teardown_package():
    global RMQ_CID, REDIS_CID
    assert RMQ_CID is not None, "No RabbitMQ container to stop."
    assert REDIS_CID is not None, "No Redis container to stop."

    remove_container(RMQ_CID)
    remove_container(REDIS_CID)
    RMQ_CID = None
    REDIS_CID = None
