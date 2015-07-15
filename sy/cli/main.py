import argparse

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

    parser_add.add_argument('cid', help='The container\'s id')
    parser_add.add_argument('stype', help='The sensor type')
    parser_del.add_argument('cid', help='The container\'s id')
    parser_del.add_argument('stype', help='The sensor type')
    #parser.add_argument('-t', dest='topic', default='sensors.*',
    #    help='The topic to subscribe to')
    args = parser.parse_args()
