import logging
from adminapp.lib.base import BaseController, render
from adminapp import model
from adminapp.model import meta
from formalchemy.ext.pylons.admin import FormAlchemyAdminController

log = logging.getLogger(__name__)

class AdminController(BaseController):
    model = model # where your SQLAlchemy mappers are
    forms = None # module containing FormAlchemy fieldsets definitions
    def Session(self): # Session factory
        return meta.Session

AdminController = FormAlchemyAdminController(AdminController)
