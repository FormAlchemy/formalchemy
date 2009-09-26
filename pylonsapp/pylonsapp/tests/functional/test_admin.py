from pylonsapp.tests import *
from pylonsapp import model
from pylonsapp.model import meta
import simplejson as json

class TestAdminController(TestController):

    def setUp(self):
        TestController.setUp(self)
        meta.engine.execute(model.foo_table.delete())

    def test_index(self):
        # index
        response = self.app.get(url('admin'))
        response.mustcontain('/admin/Foo')
        response = response.click('Foo')

        ## Simple model

        # add page
        response.mustcontain('/admin/Foo/new')
        response = response.click('New object')
        form = response.forms[0]
        form['Foo--bar'] = 'value'
        response = form.submit()
        assert response.headers['location'] == 'http://localhost/admin/Foo'

        # model index
        response = response.follow()
        response.mustcontain('<td>value</td>')

        # edit page
        response = response.click('edit')
        form = response.forms[0]
        form['Foo-1-bar'] = 'new value'
        form['_method'] = 'PUT'
        response = form.submit()
        response = response.follow()

        # model index
        response.mustcontain('<td>new value</td>')

        # delete
        response = response.forms[0].submit()
        response = response.follow()

        assert 'new value' not in response, response

    def test_fk(self):
        response = self.app.get(url('admin'))
        response.mustcontain('/admin/Animal')

        ## Animals / FK
        response = response.click('Animal')

        # add page
        response.mustcontain('/admin/Animal/new', 'New object')
        response = response.click('New object')
        response.mustcontain('<option value="1">gawel</option>')
        form = response.forms[0]
        form['Animal--name'] = 'dewey'
        form['Animal--owner_id'] = '1'
        response = form.submit()
        assert response.headers['location'] == 'http://localhost/admin/Animal'

    def test_json(self):
        # index
        response = self.app.get(url('formatted_admin', format='json'))
        response.mustcontain('"Owner": "/admin/Owner",')

        ## Simple model

        # add page
        response = self.app.post(url('models', modelname='Foo'), dict(bar='value'), extra_environ={'HTTP_ACCEPT':'application/json'})
        response.mustcontain('"bar": "value"')
        data = json.loads(response.body)

        # get data
        response = self.app.get(data['url'], extra_environ={'HTTP_ACCEPT':'application/json'})
        response.mustcontain('"bar": "value"')
        response = self.app.get('%s.json' % data['url'])
        response.mustcontain('"bar": "value"')

        # edit page
        response = self.app.put(data['url'], '{"bar": "new value"}', extra_environ={'HTTP_ACCEPT':'application/json'})
        response.mustcontain('"bar": "new value"')

        # delete
        response = self.app.delete(data['url'])


