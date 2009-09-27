from pylonsapp.tests import *

class TestOwnersController(TestController):

    def test_index(self):
        resp = self.app.get(url('owners'))
        resp.mustcontain('gawel')

        resp = self.app.get(url('formatted_owners', format='json'))
        resp.mustcontain('{"records": {"1": "/owners/1",')

    def test_add(self):
        resp = self.app.post(url('/owners.json'), {"animals": '1', "name": "gawel"})
        resp.mustcontain('"gawel"', '/owners/')

    def test_view(self):
        resp = self.app.get(url('/owners/1'))
        resp.mustcontain('gawel')

        resp = self.app.get(url('/owners/1.json'))
        resp.mustcontain('"gawel"')

    def test_edit(self):
        resp = self.app.get(url('/owners/1/edit'))
        resp.mustcontain('Edit', 'gawel')

    def test_update(self):
        resp = self.app.put(url('/owners/31.json'), '{"animals": [1], "name": "gawel"}')
        resp.mustcontain('"gawel"', '/owners/31')

