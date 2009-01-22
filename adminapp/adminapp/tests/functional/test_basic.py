from adminapp.tests import *

class TestBasicController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='basic', action='index'))
        response.mustcontain('This is the bar field')
