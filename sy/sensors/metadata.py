from sy import log
from sy.sensors.base import BaseRedisSensor
from sy.exceptions import SensorError
from docker.errors import APIError
import re

LOG = log.get(__name__)


class BaseMetadataSensor(BaseRedisSensor):
    inspect_format = ''

    def _validate_inspect_format(self):
        if re.match("^(\w+\.?\w+)*$", self.inspect_format) is None:
            raise SensorError('{}: "{}" is not a valid inspect format'.format(self.uid, self.inspect_format))

    def __init__(self, *args, **kwargs):
        self._validate_inspect_format()
        super(BaseMetadataSensor, self).__init__(*args, **kwargs)

    def _get(self):
        try:
            data = self.container.inspect()
        except APIError as e:
            LOG.error('{}: error in inspecting container: {}'.format(self.uid, e.explanation))
            return {}

        if not self.inspect_format:
            return data

        keys = self.inspect_format.split('.')
        response = data
        try:
            for k in keys:
                response = response[k]
        except KeyError as e:
            LOG.error('{}: {} is not a valid key'.format(self.uid, e.message))
            return {}

        return {keys[-1]: response}

AllMetadataSensor = BaseMetadataSensor

class IPSensor(BaseMetadataSensor):
    inspect_format = 'NetworkSettings.IPAddress'
    pass

class HostConfigSensor(BaseMetadataSensor):
    inspect_format = 'HostConfig'
    pass
