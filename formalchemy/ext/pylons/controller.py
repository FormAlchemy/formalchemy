# -*- coding: utf-8 -*-
from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons import url
from formalchemy import Grid, FieldSet

import simplejson as json

class _FieldSetController(object):

    def Session(self):
        pass

    def render(self, format='html', **kwargs):
        pass

    def render_grid(self, format='html', **kwargs):
        return self.render(format=format, is_grid=True, **kwargs)

    def render_json(self, fs=None, **kwargs):
        response.content_type = 'text/javascript'
        data = dict([(field.key, field.value) for field in fs.render_fields.values()])
        return json.dumps(data)

    def query(self):
        S = self.Session()
        return S, S.query(self.model)

    def get(self, id=None):
        S = self.Session()
        if id:
            return S, S.query(self.model).get(id)
        else:
            return S, self.model()

    def url(self, *args):
        u = url(controller=self.name)
        if args:
            u += '/' + '/'.join([str(a) for a in args])
        return u

    def index(self, format='html'):
        S, instances = self.query()
        fs = self.grid.bind(instances=instances)
        fs.readonly = True
        return self.render_grid(format=format, fs=fs, id=None)

    def create(self):
        S, model = self.get()
        fs = self.fieldset.bind(model, data=request.POST, session=S)
        if fs.validate():
            fs.sync()
            S.save(model)
            S.commit()
            redirect_to(self.url(model.id))
        action = self.url()
        return self.render(format=format, fs=fs, action=action, id=None)

    def delete(self, id, format='html'):
        S, record = self.get(id)
        S.delete(record)
        if format == 'html':
            self.redirect(self.url())
        action = self.url()
        return self.render(format=format, fs=fs, action=action, id=id)

    def show(self, id, format='html'):
        S, record = self.get(id)
        fs = self.fieldset.bind(record)
        fs.readonly = True
        return self.render(format=format, fs=fs, id=id)

    def new(self, id=None, format='html'):
        S, record = self.get(id)
        fs = self.fieldset.bind(record, session=S)
        action = self.url()
        return self.render(format=format, fs=fs, action=action, id=id)

    def edit(self, id=None, format='html'):
        S, record = self.get(id)
        fs = self.fieldset.bind(record)
        action = self.url(id)
        return self.render(format=format, fs=fs, action=action, id=id)

    def update(self, id, format='html'):
        S, model = self.get(id)
        if format == 'json':
            data = json.load(request.body)
            req = Request.blanck('/')

            for k, v in data.items():
                req.POST['%s-%s-%s' % (name, id, k)] = v
        else:
            req = request

        fs = self.fieldset.bind(model, data=req.POST)
        if fs.validate():
            fs.sync()
            S.update(model)
            S.commit()
            if format == 'html':
                redirect_to(self.url(model.id))
        action = self.url(id)
        return self.render(format=format, fs=fs, action=action, id=None)

def FieldSetController(cls, name=None, model=None, grid=None, fieldset=None):
    if not fieldset:
        fieldset = FieldSet(model)
    if not grid:
        grid = Grid(model)
    return type(cls.__name__, (cls, _FieldSetController),
                dict(name=name, model=model, grid=grid, fieldset=fieldset))

