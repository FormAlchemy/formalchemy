from pyramid.view import action

from pyramidapp.models import MyModel

class MyHandler(object):
    def __init__(self, request):
        self.request = request

    @action(renderer='mytemplate.mako')
    def index(self):
        root = MyModel.by_name('root')
        return {'root':root, 'project':'pyramidapp'}
