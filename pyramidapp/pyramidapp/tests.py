import unittest
from pyramid.config import Configurator
from pyramid import testing

import os
from webtest import TestApp
from pyramidapp import main
from paste.deploy import loadapp

dirname = os.path.abspath(__file__)
dirname = os.path.dirname(dirname)
dirname = os.path.dirname(dirname)

def _initTestingDB():
   from sqlalchemy import create_engine
   from pyramidapp.models import initialize_sql
   session = initialize_sql(create_engine('sqlite://'))
   return session

class TestController(unittest.TestCase):

    def setUp(self):
        app = loadapp('config:%s' % os.path.join(dirname, 'development.ini'))
        self.app = TestApp(app)
        self.config = Configurator(autocommit=True)
        self.config.begin()
        #_initTestingDB()

    def tearDown(self):
        self.config.end()


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
        assert resp.headers['location'] == 'http://localhost/admin/Foo', resp

        # model index
        resp = resp.follow()
        resp.mustcontain('<td>value</td>')

        # edit page
        form = resp.forms[0]
        resp = form.submit()
        form = resp.forms[0]
        form['Foo-1-bar'] = 'new value'
        #form['_method'] = 'PUT'
        resp = form.submit()
        resp = resp.follow()

        # model index
        resp.mustcontain('<td>new value</td>')

        # delete
        resp = self.app.get('/admin/Foo')
        resp.mustcontain('<td>new value</td>')
        resp = resp.forms[1].submit()
        resp = resp.follow()

        assert 'new value' not in resp, resp

    def test_json(self):
        # index
        response = self.app.get('/admin/json')
        response.mustcontain('{"models": {', '"Foo": "http://localhost/admin/Foo/json"')

        ## Simple model

        # add page
        response = self.app.post('/admin/Foo/json',
                                    {'Foo--bar': 'value'})

        data = response.json
        id = data['item_url'].split('/')[-1]

        response.mustcontain('"Foo-%s-bar": "value"' % id)


        # get data
        response = self.app.get(str(data['item_url']))
        response.mustcontain('"Foo-%s-bar": "value"' % id)

        # edit page
        response = self.app.post(str(data['item_url']), {'Foo-%s-bar' % id: 'new value'})
        response.mustcontain('"Foo-%s-bar": "new value"' % id)

        # delete
        response = self.app.delete(str(data['item_url']))



