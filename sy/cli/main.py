from gevent import monkey
monkey.patch_all()
import argparse, requests, json
from sy import config, log
from sy.api import RMQConsumer, RedisAPI

LOG = log.get(__name__)

host = config.get('sy_host')
port = config.get('sy_port')
base_url = 'http://' + host + ':' + str(port)

def _get_path(*args):
    tokens = [base_url, ]
    tokens.extend(args)
    return '/'.join(tokens)

def _print_resp(resp):
    req = resp.request
    print '[{}] {} {}'.format(req.method, req.url, resp.status_code)
    print str(resp.text)

def add(args):
    cid = args.cid
    stype = args.stype

    if not args.data:
        data = {}
    else:
        try:
            data = json.loads(args.data)
        except ValueError:
            print "ERROR: Malformed JSON given"
            return

    path = _get_path('sensors', stype)
    data.update({'cid': cid})

    _print_resp(requests.post(path, data=data))

def remove(args):
    cid = args.cid
    stype = args.stype
    path = _get_path('sensors', stype, cid)
    _print_resp(requests.delete(path))

def slist(args):
    path = _get_path('sensors')
    _print_resp(requests.get(path))

def types(args):
    path = _get_path('stypes')
    _print_resp(requests.get(path))

def rmq(args):
    host = config.get('rabbit_host')
    port = config.get('rabbit_port')
    cons = RMQConsumer(args.topic, host, port)

    try:
        for method, _, msg in cons.consume():
            print '{}: {}'.format(method.routing_key, msg)
    except KeyboardInterrupt:
        cons.close_connection()
        print 'Connection closed'

def redis(args):
    host = config.get('redis_host')
    port = config.get('redis_port')
    red = RedisAPI(host, port)
    print str(red.get(args.uid))

def main():
    parser = argparse.ArgumentParser(
        description=
            """
            Client that performs requests to Sy's Daemon.
            It allows to create, remove, list sensors and get data published by them.
            """
    )

    subparsers = parser.add_subparsers()
    parser_add = subparsers.add_parser('add', help='Create a new sensor')
    parser_del = subparsers.add_parser('remove', help='Remove an existing sensor')
    parser_list = subparsers.add_parser('list', help='List active sensors')
    parser_stypes = subparsers.add_parser('types', help='List available sensor types')
    parser_rmq = subparsers.add_parser('listen', help='Display Messages from sensors')
    parser_redis = subparsers.add_parser('get', help='Get persisted data by key')

    parser_add.add_argument('cid', help='The container\'s id')
    parser_add.add_argument('stype', help='The sensor type')
    parser_add.add_argument('--init-args', default='', dest='data', help='Other init args as JSON input')
    parser_del.add_argument('cid', help='The container\'s id')
    parser_del.add_argument('stype', help='The sensor type')
    parser_rmq.add_argument('-t', dest='topic', default='#', help='The topic to listen to')
    parser_redis.add_argument('uid', help='The uid of the active sensor that is persisting data (`sy list` to get uids)')

    parser_add.set_defaults(func=add)
    parser_del.set_defaults(func=remove)
    parser_list.set_defaults(func=slist)
    parser_stypes.set_defaults(func=types)
    parser_rmq.set_defaults(func=rmq)
    parser_redis.set_defaults(func=redis)

    args = parser.parse_args()
    args.func(args)
