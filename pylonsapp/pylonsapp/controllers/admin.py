import logging
from pylonsapp.lib.base import BaseController, render
from pylonsapp import model
from pylonsapp import forms
from pylonsapp.model import meta
from formalchemy.ext.pylons.controller import ModelsController

log = logging.getLogger(__name__)

class AdminControllerBase(BaseController):
    model = model # where your SQLAlchemy mappers are
    forms = forms # module containing FormAlchemy fieldsets definitions
    def Session(self): # Session factory
        return meta.Session

AdminController = ModelsController(AdminControllerBase,
                                   prefix_name='admin',
                                   member_name='model',
                                   collection_name='models')

