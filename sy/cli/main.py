import argparse
from sy.cli import rmq

def main():
    parser = argparse.ArgumentParser(description='Sy client to have a look at monitored data.')
    parser.add_argument('-t', dest='topic', default='sensors.*',
        help='The topic to subscribe to')
    args = parser.parse_args()
