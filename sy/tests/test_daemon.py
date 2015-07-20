from gevent import monkey
monkey.patch_all()
from sy import daemon
from sy.sensors.base import get_uid
from sy.sensors import TYPES
from unittest import TestCase
import json

class DaemonTestCase(TestCase):
    def setUp(self):
        self.daemon = daemon.daemon.test_client()
        self.status = daemon._status

    def tearDown(self):
        # flush all sensors
        for _, sensor in self.status.sensors.items():
            sensor.kill()
        self.status.sensors = {}

    def test_add_dummy_sensor(self):
        data = {
            'cid': 'fake-container',
        }
        resp = self.daemon.post('/sensors/dummy', data=data)
        self.assertEquals(resp.status_code, 201)

        resp_data = json.loads(resp.data)['sensor']
        self.assertTrue('cid' in resp_data.keys())
        self.assertTrue('uid' in resp_data.keys())
        self.assertTrue('spacing' in resp_data.keys())
        uid = get_uid(TYPES['dummy'], resp_data['cid'])
        self.assertEquals(uid, resp_data['uid'])

    def test_add_wrong_data(self):
        # empty
        data = {}
        resp = self.daemon.post('/sensors/dummy', data=data)
        self.assertEquals(resp.status_code, 400)
        # more args
        data = {
            'cid': 'fake-container',
            'i_am_supposed': 'not_to_be_here',
        }
        resp = self.daemon.post('/sensors/dummy', data=data)
        self.assertEquals(resp.status_code, 400)
        # nothing has been added
        resp = self.daemon.get('/sensors')
        resp_data = json.loads(resp.data)
        self.assertEquals(dict(), resp_data)

    def test_remove_sensor(self):
        stype = 'dummy'
        cid = 'fake-container'

        resp = self.daemon.post('/sensors/' + stype, data={'cid': cid})
        self.assertEquals(resp.status_code, 201)

        path = '/'.join(['/sensors', stype, cid])
        resp = self.daemon.delete(path)
        self.assertEquals(resp.status_code, 204)

    def test_remove_non_existing_container(self):
        stype = 'dummy'
        cid = 'fake-container'

        path = '/'.join(['/sensors', stype, cid])
        resp = self.daemon.delete(path)
        self.assertEquals(resp.status_code, 400)

    def test_invalid_stype(self):
        # on add
        data = {'cid': 'fake-container'}
        resp = self.daemon.post('/sensors/invalid-stype', data=data)
        self.assertEquals(resp.status_code, 400)
        # creating container to be sure
        # that only wrong stype is causing 400
        resp = self.daemon.post('/sensors/dummy', data=data)
        self.assertEquals(resp.status_code, 201)
        # on remove
        resp = self.daemon.delete('/sensors/invalid-stype/fake-container')
        self.assertEquals(resp.status_code, 400)
