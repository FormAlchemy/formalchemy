from adminapp.tests import *

class TestAdminController(TestController):

    def setUp(self):
        TestController.setUp(self)
        meta.engine.execute(model.foo_table.delete())

    def test_index(self):
        # index
        response = self.app.get(url(controller='admin'))
        response.mustcontain('/admin/Foo')
        response = response.click('Foo')

        # add page
        response.mustcontain('/admin/Foo/edit')
        response = response.click('Create form')
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
        response = form.submit()
        response = response.follow()

        # model index
        response.mustcontain('<td>new value</td>')

        # delete
        response = response.click('delete')
        response = response.follow()

        assert 'new value' not in response, response
