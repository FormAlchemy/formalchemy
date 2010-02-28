import logging

from pylons import request, response, session, url, tmpl_context as c
from pylons.controllers.util import abort, redirect

from pylonsapp.lib.base import BaseController, render
from pylonsapp import model
from pylonsapp.model import meta

from formalchemy.ext.pylons.controller import RESTController

log = logging.getLogger(__name__)

class OwnersController(BaseController):

    def Session(self):
        return meta.Session

    def get_model(self):
        return model.Owner

OwnersController = RESTController(OwnersController, 'owner', 'owners')
