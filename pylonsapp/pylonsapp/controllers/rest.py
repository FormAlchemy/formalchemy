import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from pylonsapp.lib.base import BaseController, render
from pylonsapp import model
from pylonsapp.model import meta

from formalchemy.ext.pylons.controller import FieldSetController

log = logging.getLogger(__name__)

class RestController(BaseController):

    def Session(self):
        return meta.Session

    def render(self, format='html', **kwargs):
        if format == 'json':
            return self.render_json(**kwargs)
        return render('/rest.mako', extra_vars=kwargs)

    def render_grid(self, format='html', **kwargs):
        return render('/rest.mako', extra_vars=kwargs)

RestController = FieldSetController(RestController, 'rest', model.Owner)
