# -*- coding: utf-8 -*-
__doc__ = """This module provide a RESTful controller for formalchemy's FieldSets.
"""
from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons.templating import render_mako as render
from pylons import url
from formalchemy.fields import _pk
from webhelpers.paginate import Page
from formalchemy import Grid, FieldSet
from formalchemy.i18n import get_translator
from formalchemy.fields import Field
from formalchemy import fatypes

import simplejson as json

class _FieldSetController(object):

    template = '/restfieldset.mako'

    def Session(self):
        """return a Session object. You **must** override this."""
        raise NotImplementedError()

    def get_model(self):
        """return SA mapper class. You **must** override this."""
        raise NotImplementedError()

    def sync(self, fs, id=None):
        """sync a record. If ``id`` is None add a new record else save current one.

        Default is:

        .. sourcecode:: py

            S = self.Session()
            if id:
                S.update(fs.model)
            else:
                S.add(fs.model)
            S.commit()
        """
        S = self.Session()
        if id:
            S.update(fs.model)
        else:
            S.add(fs.model)
        S.commit()

    def render(self, format='html', **kwargs):
        """render the form as html or json"""
        if format == 'json':
            return self.render_json(**kwargs)
        return render(self.template, extra_vars=kwargs)

    def render_grid(self, format='html', **kwargs):
        """render the grid as html or json"""
        return self.render(format=format, is_grid=True, **kwargs)

    def render_json(self, fs=None, **kwargs):
        response.content_type = 'text/javascript'
        if fs:
            fields = dict([(field.key, field.model_value) for field in fs.render_fields.values()])
            data = dict(fields=fields)
            pk = _pk(fs.model)
            if pk:
                data['url'] = self.url(pk)
        else:
            data = {}
        data.update(kwargs)
        return json.dumps(data)

    def query(self):
        """return an iterable used for index listing.

        Default is:

        .. sourcecode:: py

            S = self.Session()
            return S.query(self.get_model())
        """
        S = self.Session()
        return S.query(self.get_model())

    def get(self, id=None):
        """return correct record for ``id``.

        Default is:

        .. sourcecode:: py

            S = self.Session()
            model = self.get_model()
            if id:
                return S.query(model).get(id)
            else:
                return model()
        """
        S = self.Session()
        model = self.get_model()
        if id:
            return S.query(model).get(id)
        else:
            return model()

    def get_fieldset(self, id=None):
        """return a FieldSet object bound to the correct record for ``id``.

        Default is:

        .. sourcecode:: py

            fs = FieldSet(self.get(id))
            fs.__name__ = fs.model.__class__.__name__
            return fs
        """
        fs = FieldSet(self.get(id))
        fs.__name__ = fs.model.__class__.__name__
        return fs

    def get_grid(self):
        """return a Grid object"""
        grid = Grid(self.get_model())
        def edit_link():
            return lambda item: '''<form action="%(url)s" method="GET">
                                    <input type="submit" class="icon edit" title="%(label)s" value="%(label)s" />
                                    </form>
                                ''' % dict(
                                url=url('edit_%s' % self.singular, id=_pk(item)),
                                label=get_translator().gettext('edit'))
        def delete_link():
            return lambda item: '''<form action="%(url)s" method="POST">
                                    <input type="submit" class="icon delete" title="%(label)s" value="%(label)s" />
                                    <input type="hidden" name="_method" value="DELETE" />
                                    </form>
                                ''' % dict(
                                    url=url(self.singular, id=_pk(item)),
                                    label=get_translator().gettext('delete'))
        grid.append(Field('edit', fatypes.String, edit_link()))
        grid.append(Field('delete', fatypes.String, delete_link()))
        grid.readonly = True
        return grid

    def url(self, *args):
        """return url for the controller and add args to path"""
        u = url(controller=self.plural)
        if args:
            u += '/' + '/'.join([str(a) for a in args])
        return u

    def index(self, format='html'):
        query = self.query()
        page = Page(query, page=int(request.GET.get('page', '1')))
        if format == 'json':
            values = []
            for item in page:
                pk = _pk(item)
                values.append((pk, url(self.singular, id=pk)))
            return self.render_json(records=dict(values), page_count=page.page_count, page=page.page)
        fs = self.get_grid()
        fs = fs.bind(instances=page)
        fs.readonly = True
        return self.render_grid(format=format, page=page, fs=fs, id=None)

    def create(self):
        fs = self.get_fieldset()
        if fs.validate():
            fs.sync()
            self.sync(fs)
            redirect_to(self.url())
        action = self.url()
        return self.render(format=format, fs=fs, action=action, id=None)

    def delete(self, id, format='html'):
        S, record = self.get(id)
        if record:
            S.delete(record)
            S.commit()
        if format == 'html':
            redirect_to(self.url())
        action = self.url()
        return self.render(format=format, fs=fs, action=action, id=id)

    def show(self, id, format='html'):
        fs = self.get_fieldset(id)
        fs.readonly = True
        return self.render(format=format, fs=fs, id=id)

    def new(self, id=None, format='html'):
        fs = self.get_fieldset(id)
        fs = fs.bind(session=S)
        action = self.url()
        return self.render(format=format, fs=fs, action=action, id=id)

    def edit(self, id=None, format='html'):
        fs = self.get_fieldset(id)
        action = self.url(id)
        return self.render(format=format, fs=fs, action=action, id=id)

    def update(self, id, format='html'):
        fs = self.get_fieldset(id)
        if format == 'json':
            data = json.load(request.body_file)
            request.body = ''
            if hasattr(fs, 'model'):
                # this should bread if fs is a non standard fieldset
                name = fs.model.__class__.__name__
                for k, v in data.items():
                    if isinstance(v, list):
                        for val in v:
                            request.POST.add('%s-%s-%s' % (name, id, k), str(val))
                    else:
                        request.POST.add('%s-%s-%s' % (name, id, k), str(v))

        fs = fs.bind(data=request.POST)
        if fs.validate():
            fs.sync()
            self.sync(fs, id)
            if format == 'html':
                redirect_to(self.url(id))
            else:
                return self.render(format=format, fs=fs, status=0)
        if format == 'html':
            action = self.url(id)
            return self.render(format=format, fs=fs, action=action, id=None)
        else:
            return self.render(format=format, fs=fs, status=1)

def FieldSetController(cls, singular, plural):
    """wrap a controller with :class:~formalchemy.ext.pylons.controller._FieldSetController"""
    return type(cls.__name__, (cls, _FieldSetController),
                dict(singular=singular, plural=plural))

