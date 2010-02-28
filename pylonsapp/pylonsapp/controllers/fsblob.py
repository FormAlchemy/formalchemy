import logging
from pylons import request, response, session, url, tmpl_context as c
from pylons.controllers.util import abort, redirect
from pylonsapp.lib.base import BaseController, render
from pylonsapp.model import meta
from pylonsapp import model
from pylonsapp.forms.fsblob import Files

log = logging.getLogger(__name__)

class FsblobController(BaseController):

    def index(self, id=None):
        if id:
            record = meta.Session.query(model.Files).filter_by(id=id).first()
        else:
            record = model.Files()
        assert record is not None, repr(id)
        c.fs = Files.bind(record, data=request.POST or None)
        if request.POST and c.fs.validate():
            c.fs.sync()
            if id:
                meta.Session.update(record)
            else:
                meta.Session.add(record)
            meta.Session.commit()
            redirect(url.current(id=record.id))
        return render('/form.mako')
