from sy import log
from sy.sensors.base import BaseRMQSensor
from sy.exceptions import SensorError
from docker.errors import APIError
import psutil

LOG = log.get(__name__)
ALLOWED_USAGE_FNS = [
    'cpu_percent',
    'memory_percent',
    'num_threads',
    'io_counters',
]


class BaseUsageSensor(BaseRMQSensor):
    # TODO should specify parameters for functions
    usage_fn_names = ()

    def _validate_usage_fns(self):
        for name in self.usage_fn_names:
            if not name in ALLOWED_USAGE_FNS:
                raise SensorError('{}: {} is not an allowed usage function'.format(
                    self.__class__.__name__, name))

    def __init__(self, *args, **kwargs):
        self._validate_usage_fns()
        super(BaseUsageSensor, self).__init__(*args, **kwargs)

    def _get(self):
        try:
            top = self.container.top()
        except APIError as e:
            LOG.error('{}: error in docker top on container: {}'.format(self.uid, e.explanation))
            return {}

        pid_index = top['Titles'].index('PID')
        cmd_index = top['Titles'].index('CMD')
        processes = top['Processes']
        data = {}
        tot_usages = {fn: 0 for fn in self.usage_fn_names}

        for proc in processes:
            pid = int(proc[pid_index])
            cmd = proc[cmd_index]
            p = psutil.Process(pid)
            usages = {fn_name: getattr(p, fn_name)() for fn_name in self.usage_fn_names}

            data[pid] = {
                'cmd': cmd,
                'usage': usages
            }

            for fn_name, value in usages.items():
                tot_usages[fn_name] += value

        data['tot'] = tot_usages
        return data


class CPUPercSensor(BaseUsageSensor):
    usage_fn_names = ('cpu_percent', )
    pass


class MemoryPercSensor(BaseUsageSensor):
    usage_fn_names = ('memory_percent', )
    pass


class CPUMemoryPercSensor(BaseUsageSensor):
    usage_fn_names = ('cpu_percent', 'memory_percent')
    pass
