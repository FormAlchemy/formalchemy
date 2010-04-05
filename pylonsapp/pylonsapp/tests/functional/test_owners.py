from pylonsapp.tests import *

class TestOwnersController(TestController):

    def test_index(self):
        resp = self.app.get(url('owners'))
        resp.mustcontain('gawel')

        resp = self.app.get(url('formatted_owners', format='json'))
        resp.mustcontain('{"records": [{"url": "/owners/1", "pk": 1, "value": "gawel"}')

    def test_add(self):
        resp = self.app.post(url('/owners.json'), {"Owner--animals": '1', "Owner--name": "gawel"})
        resp.mustcontain('"gawel"', '/owners/')

    def test_view(self):
        resp = self.app.get(url('/owners/1'))
        resp.mustcontain('gawel')

        resp = self.app.get(url('/owners/1.json'))
        resp.mustcontain('"gawel"')

    def test_edit(self):
        resp = self.app.get(url('/owners/1/edit'))
        resp.mustcontain('<form action="/owners/1" method="POST" enctype="multipart/form-data">',
                         'gawel')

    def test_update(self):
        resp = self.app.put(url('/owners/31.json'), '{"Owner-31-animals": [1], "Owner-31-name": "gawel"}')
        resp.mustcontain('"gawel"', '/owners/31')

