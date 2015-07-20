import argparse, sys, os
from sy import config, log
from sy.sensors import TYPES
from sy.sensors.base import get_uid
from sy.exceptions import SensorError, DaemonError, InvalidSensorType, NoSensorFound, BadJsonInput
from schematics.exceptions import ValidationError, ConversionError
from flask import Flask, jsonify, request
import subprocess as sp


LOG = log.get(__name__)
_endpoints = ['index', 'get_sensor_types', 'get_sensors', 'add_sensor', 'del_sensor']
daemon = Flask(__name__)

def validate_stype(stype):
    if stype not in TYPES:
        raise InvalidSensorType(stype)


class SensorsStatus(object):
    def __init__(self):
        super(SensorsStatus, self).__init__()
        self.sensors = {} # dict sensor_uid: sensor_object

    def add(self, init_dict, stype):
        """
        See `sy.sensors` for available
        sensor types (`__init__.py`).
        """
        sensor_class = TYPES[stype]
        sensor = sensor_class(init_dict)
        # if init_dict is malformed, this will
        # raise a ModelValidationError (subclass of ValidationError)
        sensor.validate()
        uid = sensor.uid
        warn = ''

        if uid in self.sensors:
            warn = 'No need to start sensor, {} sensor for {} container already exists.'.format(stype, sensor.cid)
            LOG.warning(warn)
            return self.sensors[uid], warn

        # we can add the new sensor
        sensor.start()
        self.sensors[uid] = sensor
        return sensor, warn

    def remove(self, cid, stype):
        sensor_class = TYPES[stype]
        uid = get_uid(sensor_class, cid)
        try:
            self.sensors[uid].kill()
            del self.sensors[uid]
        except KeyError:
            raise NoSensorFound(cid, stype)


_status = SensorsStatus()

@daemon.errorhandler(DaemonError)
def handle_wrong_json_input(error):
    LOG.error(error.message)
    resp = jsonify(error.to_dict())
    resp.status_code = 400
    return resp

@daemon.errorhandler(SensorError)
@daemon.errorhandler(ValidationError)
@daemon.errorhandler(ConversionError)
def handle_validation_error(error):
    LOG.error(error.message)
    resp = jsonify({'message': error.message})
    resp.status_code = 400
    return resp

@daemon.route('/', methods=['GET',])
def index():
    """
    / (`GET`)

    Returns an endpoint map.
    """
    body = {
        endpoint: getattr(sys.modules[__name__], endpoint).__doc__
        for endpoint in _endpoints
    }
    return jsonify(body)

@daemon.route('/stypes', methods=['GET',])
def get_sensor_types():
    """
    /stypes (`GET`)

    Returns a map of all sensor types.
    """
    return jsonify({t: c.__module__ + '.' + c.__name__ for t, c in TYPES.items()})

@daemon.route('/sensors', methods=['GET',])
def get_sensors():
    """
    /sensors (`GET`)

    Returns all active sensors.
    """
    global _status
    body = { s.uid: 'ALIVE' if not s.dead else 'DEAD'
             for s in _status.sensors.values()}
    return jsonify(body)

@daemon.route('/sensors/<stype>', methods=['POST',])
def add_sensor(stype):
    """
    /sensors/<sensor_type> (`POST`)

    Adds and starts a new sensor from the given json input.
    Example:
    {
        "cid": "container name or id",
    }
    """
    global _status
    validate_stype(stype)
    sensor, warn = _status.add(request.form, stype)
    status = 201 if not warn else 200
    data = {
        'sensor': sensor.to_primitive(),
        'warning': warn
    }

    if not warn:
        LOG.info('Sensor created: {}'.format(sensor.to_primitive()))

    body = jsonify(data)
    return body, status

@daemon.route('/sensors/<stype>/<cid>', methods=['DELETE',])
def del_sensor(stype, cid):
    """
    /sensors/<sensor_type>/<container_id> (`DELETE`)

    Stops and removes an active sensor from the given input.
    Example:
    {
        "cid": "container id or name",
        "stype": "the type of the sensor to be stopped"
    }
    """
    global _status
    validate_stype(stype)
    _status.remove(cid, stype)
    LOG.info('Sensor with cid {} and type {} deleted'.format(cid, stype))
    return '', 204

def run():
    parser = argparse.ArgumentParser(
        description="Client to start Sy's daemon."
    )

    parser.add_argument('-d', dest='daemon', action='store_true', help='Start server as daemon')
    parser.add_argument('-D', dest='debug', action='store_true', help='Start server in debug mode')
    args = parser.parse_args()
    daemon.debug = args.debug
    port = config.get('sy_port')

    if args.daemon:
        #TODO handle better command string
        cmd = 'python bin/sy-agent'
        if args.debug:
            cmd += ' -D'

        DEVNULL = open(os.devnull, 'wb')
        p = sp.Popen(cmd.split(), stdout=DEVNULL, stderr=DEVNULL)

        LOG.debug('Daemon\'s PID: {}'.format(p.pid))
    else:
        daemon.run(port=port)
