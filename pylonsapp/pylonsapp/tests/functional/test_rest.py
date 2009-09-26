from pylonsapp.tests import *

class TestRestController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='rest', action='index'))
        # Test response...
