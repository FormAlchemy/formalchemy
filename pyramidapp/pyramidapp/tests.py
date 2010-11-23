import os
import unittest
from webtest import TestApp
from pyramidapp import main
from paste.deploy import loadapp

dirname = os.path.abspath(__file__)
dirname = os.path.dirname(dirname)
dirname = os.path.dirname(dirname)

class TestController(unittest.TestCase):

    def setUp(self):
        app = loadapp('config:%s' % os.path.join(dirname, 'development.ini'))
        self.app = TestApp(app)

    def test_index(self):
        # index
        resp = self.app.get('/admin/')
        resp.mustcontain('/admin/Foo')
        resp = resp.click('Foo')

        ## Simple model

        # add page
        resp.mustcontain('/admin/Foo/new')
        resp = resp.click('New Foo')
        resp.mustcontain('/admin/Foo"')
        form = resp.forms[0]
        form['Foo--bar'] = 'value'
        resp = form.submit()
        assert resp.headers['location'] == 'http://localhost/admin/Foo'

        # model index
        resp = resp.follow()
        resp.mustcontain('<td>value</td>')

        # edit page
        form = resp.forms[0]
        resp = form.submit()
        form = resp.forms[0]
        form['Foo-1-bar'] = 'new value'
        form['_method'] = 'PUT'
        resp = form.submit()
        resp = resp.follow()

        # model index
        resp.mustcontain('<td>new value</td>')

        # delete
        resp = self.app.get(url('models', model_name='Foo'))
        resp.mustcontain('<td>new value</td>')
        resp = resp.forms[1].submit()
        resp = resp.follow()

        assert 'new value' not in resp, resp



class MyHandlerTests(unittest.TestCase):
    def setUp(self):
        from pyramid.configuration import Configurator
        from pyramidapp.models import initialize_sql
        self.session = initialize_sql('sqlite://')
        self.config = Configurator()
        self.config.begin()

    def tearDown(self):
        self.config.end()

    def _makeOne(self, request):
        from pyramidapp.handlers import MyHandler
        return MyHandler(request)

    def test_index(self):
        request = DummyRequest()
        handler = self._makeOne(request)
        info = handler.index()
        self.assertEqual(info['project'], 'pyramidapp')
        self.assertEqual(info['root'].name, 'root')

class DummyRequest(object):
    pass
