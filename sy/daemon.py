from gevent import monkey
monkey.patch_all()
import sys
from sy import config, log
from sy.sensors import TYPES
from sy.sensors.base import get_uid
from sy.exceptions import SensorError, DaemonError, InvalidSensorType, NoSensorFound, BadJsonInput
from schematics.exceptions import ValidationError, ConversionError
from flask import Flask, jsonify, request

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

        if uid in self.sensors:
            LOG.info('No need to start sensor, {} sensor for {} container already exists.'.format(stype, sensor.cid))
            return sensor

        # we can add the new sensor
        sensor.start()
        self.sensors[uid] = sensor
        return sensor

    def remove(self, cid, stype):
        sensor_class = TYPES[stype]
        uid = get_uid(sensor_class, cid)
        try:
            self.sensors[uid].kill()
            del self.sensors[uid]
        except KeyError:
            raise NoSensorFound(cid, stype)


status = SensorsStatus()

@daemon.errorhandler(DaemonError)
def handle_wrong_json_input(error):
    resp = jsonify(error.to_dict())
    resp.status_code = 400
    return resp

@daemon.errorhandler(SensorError)
@daemon.errorhandler(ValidationError)
@daemon.errorhandler(ConversionError)
def handle_validation_error(error):
    resp = jsonify(error.message)
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
    body = { s.uid: 'ALIVE' if not s.dead else 'DEAD'
             for s in status.sensors.values()}
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
    validate_stype(stype)
    sensor = status.add(request.form, stype)
    LOG.info('Sensor created: {}'.format(sensor.to_primitive()))
    body = jsonify(sensor.to_primitive())
    return body, 201

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
    validate_stype(stype)
    status.remove(cid, stype)
    LOG.info('Sensor with cid {} and type {} deleted'.format(cid, stype))
    return '', 204

if __name__ == '__main__':
    daemon.debug = True
    daemon.run()
