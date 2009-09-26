from pylonsapp.tests import *

class TestRestController(TestController):

    def test_index(self):
        resp = self.app.get(url(controller='rest', action='index'))
        resp.mustcontain('gawel')

    def test_view(self):
        resp = self.app.get(url('/rest/1'))
        resp.mustcontain('gawel')

        resp = self.app.get(url('/rest/1.json'))
        resp.mustcontain('"gawel"')

    def test_edit(self):
        resp = self.app.get(url('/rest/1/edit'))
        resp.mustcontain('Edit', 'gawel')

    def test_update(self):
        resp = self.app.put(url('/rest/1.json'), '{"animals": [1], "name": "gawel"}')
        resp.mustcontain('"gawel"')

