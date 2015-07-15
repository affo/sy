import sys, json
from sy import config, log
from sy.sensors import TYPES
from sy.sensors.base import get_uid
from sy.exceptions import DaemonError, InvalidSensorType, NoSensorFound, BadJsonInput
from flask import Flask, jsonify, request

LOG = log.get(__name__)
_endpoints = ['index', 'get_sensor_types', 'get_sensors', 'add_sensor', 'del_sensor']
daemon = Flask(__name__)

def validate_request():
    req_data = request.form
    allowed_keys = ('cid', 'stype')
    request_errors = []

    for k in req_data.keys():
        if k not in allowed_keys:
            request_errors.append(k)

    if request_errors:
        raise BadJsonInput(
            request_errors,
            method=request.method,
            url=request.path,
        )


class SensorsStatus(object):
    def __init__(self):
        super(SensorsStatus, self).__init__()
        self.sensors = {} # dict sensor_uid: sensor_object

    def add(self, cid, stype):
        """
        See `sy.sensors` for available
        sensor types (`__init__.py`).
        """
        if stype not in TYPES:
            raise InvalidSensorType(stype)

        sensor_class = TYPES[stype]
        uid = get_uid(sensor_class, cid)
        if uid in self.sensors:
            LOG.info('No need to start sensor, {} sensor for {} container already exists.'.format(stype, cid))
            return uid

        # we can add the new sensor
        sensor = sensor_class(cid)
        sensor.start()
        self.sensors[uid] = sensor
        return uid

    def remove(self, cid, stype):
        if stype not in TYPES:
            raise InvalidSensorType(stype)

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

@daemon.route('/sensors', methods=['POST',])
def add_sensor():
    """
    /sensors (`POST`)

    Adds and starts a new sensor from the given json input.
    Example:
    {
        "cid": "container name or id",
        "stype": "one of the available sensors types"
    }
    """
    validate_request(request.form)

    cid = request.form['cid']
    stype = request.form['stype']
    uid = status.add(cid, stype)
    return jsonify({'uid': uid}), 201

@daemon.route('/sensors', methods=['DELETE',])
def del_sensor():
    """
    /sensors (`DELETE`)

    Stops and removes an active sensor from the given input.
    Example:
    {
        "cid": "container id or name",
        "stype": "the type of the sensor to be stopped"
    }
    """
    validate_request(request.form)

    cid = request.form['cid']
    stype = request.form['stype']
    status.remove(cid, stype)
    return '', 204

if __name__ == '__main__':
    daemon.debug = True
    daemon.run()
