from pylonsapp.tests import *
from pylonsapp import model
from pylonsapp.model import meta
import simplejson as json

class TestAdminController(TestController):

    def setUp(self):
        TestController.setUp(self)
        meta.Session.bind.execute(model.foo_table.delete())

    def test_index(self):
        # index
        response = self.app.get(url('admin'))
        response.mustcontain('/admin/Foo/models')
        response = response.click('Foo')

        ## Simple model

        # add page
        response.mustcontain('/admin/Foo/models/new')
        response = response.click('New Foo')
        form = response.forms[0]
        form['Foo--bar'] = 'value'
        response = form.submit()
        assert response.headers['location'] == 'http://localhost/admin/Foo/models'

        # model index
        response = response.follow()
        response.mustcontain('<td>value</td>')

        # edit page
        form = response.forms[0]
        response = form.submit()
        form = response.forms[0]
        form['Foo-1-bar'] = 'new value'
        form['_method'] = 'PUT'
        response = form.submit()
        response = response.follow()

        # model index
        response.mustcontain('<td>new value</td>')

        # delete
        response = self.app.get(url('models', model_name='Foo'))
        response.mustcontain('<td>new value</td>')
        response = response.forms[1].submit()
        response = response.follow()

        assert 'new value' not in response, response

    def test_fk(self):
        response = self.app.get(url('admin'))
        response.mustcontain('/admin/Animal/models')

        ## Animals / FK
        response = response.click('Animal')

        # add page
        response.mustcontain('/admin/Animal/models/new', 'New Animal')
        response = response.click('New Animal')
        response.mustcontain('<option value="1">gawel</option>')
        form = response.forms[0]
        form['Animal--name'] = 'dewey'
        form['Animal--owner_id'] = '1'
        response = form.submit()
        assert response.headers['location'] == 'http://localhost/admin/Animal/models'

    def test_json(self):
        # index
        response = self.app.get(url('formatted_admin', format='json'))
        response.mustcontain('{"models": {"Files": "/admin/Files/models",')

        ## Simple model

        # add page
        response = self.app.post(url('formatted_models', model_name='Foo', format='json'), dict(bar='value'))
        response.mustcontain('"bar": "value"')
        data = json.loads(response.body)

        # get data
        response = self.app.get('%s.json' % data['url'])
        response.mustcontain('"bar": "value"')

        # edit page
        response = self.app.put('%s.json' % data['url'], '{"bar": "new value"}')
        response.mustcontain('"bar": "new value"')

        # delete
        response = self.app.delete('%s.json' % data['url'])


