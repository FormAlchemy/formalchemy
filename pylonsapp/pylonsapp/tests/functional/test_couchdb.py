from pylonsapp.tests import *
from couchdbkit import Server

try:
    server = Server()
    if server: pass
except:
    server = None
else:
    try:
        server.delete_db('formalchemy_test')
    except:
        pass
    db = server.get_or_create_db('formalchemy_test')

def couchdb_runing(func):
    if server:
        return func
    else:
        def f(self): pass
        return f

class TestCouchdbController(TestController):

    @couchdb_runing
    def test_index(self):
        response = self.app.get(url('couchdb'))
        response.mustcontain('/couchdb/Pet/nodes')
        response = response.click('Pet')

        response.mustcontain('/couchdb/Pet/nodes/new')
        response = response.click('New Pet')
        form = response.forms[0]
        form['Pet--name'] = 'value'
        form['Pet--type'] = 'cat'
        response = form.submit()
        assert response.headers['location'] == 'http://localhost/couchdb/Pet/nodes'

        # model index
        response = response.follow()
        response.mustcontain('<td>value</td>')

        # edit page
        form = response.forms[0]
        response = form.submit()
        form = response.forms[0]
        for k in form.fields.keys():
            if k and k.endswith('name'):
                form[k] = 'new value'
        form['_method'] = 'PUT'
        response = form.submit()
        response = response.follow()

        # model index
        response.mustcontain('<td>new value</td>')

        # delete
        response = self.app.get(url('nodes', model_name='Pet'))
        response.mustcontain('<td>new value</td>')
        response = response.forms[1].submit()
        response = response.follow()

        assert 'new value' not in response, response
