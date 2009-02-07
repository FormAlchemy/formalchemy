from pylonsapp.tests import *
from pylonsapp import model
from pylonsapp.model import meta
from pylons import config
import os

class TestFsblobController(TestController):

    def setUp(self):
        TestController.setUp(self)
        meta.engine.execute(model.files_table.delete())

    def test_index(self):
        # form
        response = self.app.get(url(controller='fsblob', action='index'))
        response.mustcontain('Files--path')

        # test post file
        response = self.app.post(url(controller='fsblob', action='index'),
                                 upload_files=[('Files--path', 'test.txt', 'My test\n')])
        response = response.follow()
        response.mustcontain('Remove')

        # get file with http
        fresponse = response.click('test.txt')
        assert fresponse.headers['content-type'] == 'text/plain'
        fresponse.mustcontain('My test')

        # assume storage
        fpath = os.path.join(config['app_conf']['storage_path'],
                fresponse.request.path_info[1:])

        assert os.path.isfile(fpath), fpath

        # remove
        form = response.form
        form['Files-1-path'] = ''
        form['Files-1-path--remove'] = True
        response = form.submit()
        response.mustcontain('Please enter a value')
        assert 'test.txt' not in response, response

