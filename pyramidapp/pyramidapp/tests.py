import unittest

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
