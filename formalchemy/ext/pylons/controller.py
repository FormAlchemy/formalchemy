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
    engine = None

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
        kwargs.update(collection=self.plural, member=self.singular)
        if self.engine:
            return self.engine.render(self.template, **kwargs)
        else:
            return render(self.template, extra_vars=kwargs)

    def render_grid(self, format='html', **kwargs):
        """render the grid as html or json"""
        return self.render(format=format, is_grid=True, **kwargs)

    def render_json(self, fs=None, **kwargs):
        response.content_type = 'text/javascript'
        if fs:
            try:
                fields = fs.jsonify()
            except AttributeError:
                fields = dict([(field.key, field.model_value) for field in fs.render_fields.values()])
            data = dict(fields=fields)
            pk = _pk(fs.model)
            if pk:
                data['url'] = self.url(pk)
        else:
            data = {}
        data.update(kwargs)
        return json.dumps(data)

    def get_page(self):
        """return a ``webhelpers.paginate.Page`` used to display ``Grid``.

        Default is:

        .. sourcecode:: py

            S = self.Session()
            query = S.query(self.get_model())
            return Page(query, page=int(request.GET.get('page', '1')))
        """
        S = self.Session()
        query = S.query(self.get_model())
        return Page(query, page=int(request.GET.get('page', '1')))

    def get(self, id=None):
        """return correct record for ``id`` or a new instance.

        Default is:

        .. sourcecode:: py

            S = self.Session()
            model = self.get_model()
            if id:
                model = S.query(model).get(id)
            else:
                model = model()
            return model or abort(404)

        """
        S = self.Session()
        model = self.get_model()
        if id:
            model = S.query(model).get(id)
        else:
            model = model()
        return model or abort(404)

    def get_fieldset(self, id=None):
        """return a ``FieldSet`` object bound to the correct record for ``id``.

        Default is:

        .. sourcecode:: py

            fs = FieldSet(self.get(id))
            fs.__name__ = fs.model.__class__.__name__
            fs.engine = self.engine
            return fs
        """
        fs = FieldSet(self.get(id))
        fs.__name__ = fs.model.__class__.__name__
        fs.engine = self.engine
        return fs

    def get_add_fieldset(self):
        """return a ``FieldSet`` used for add form.

        Default is:

        .. sourcecode:: py
            fs = self.get_fieldset()
            for field in fs.render_fields.itervalues():
                if field.is_readonly():
                    del fs[field.name]
            return fs
        """
        fs = self.get_fieldset()
        for field in fs.render_fields.itervalues():
            if field.is_readonly():
                del fs[field.name]
        return fs

    def get_grid(self):
        """return a Grid object

        Default is:

        .. sourcecode:: py

            grid = Grid(self.get_model())
            grid.engine = self.engine
            self.update_grid(grid)
            return grid
        """
        grid = Grid(self.get_model())
        grid.engine = self.engine
        self.update_grid(grid)
        return grid


    def update_grid(self, grid):
        """Add edit and delete buttons to ``Grid``"""
        try:
            grid.edit
        except AttributeError:
            def edit_link():
                return lambda item: '''
                <form action="%(url)s" method="GET" class="ui-grid-icon ui-widget-header ui-corner-all">
                <input type="submit" class="ui-grid-icon ui-icon ui-icon-pencil" title="%(label)s" value="%(label)s" />
                </form>
                ''' % dict(url=url('edit_%s' % self.singular, id=_pk(item)),
                            label=get_translator().gettext('edit'))
            def delete_link():
                return lambda item: '''
                <form action="%(url)s" method="POST" class="ui-grid-icon ui-state-error ui-corner-all">
                <input type="submit" class="ui-icon ui-icon-circle-close" title="%(label)s" value="%(label)s" />
                <input type="hidden" name="_method" value="DELETE" />
                </form>
                ''' % dict(url=url(self.singular, id=_pk(item)),
                           label=get_translator().gettext('delete'))
            grid.append(Field('edit', fatypes.String, edit_link()))
            grid.append(Field('delete', fatypes.String, delete_link()))
            grid.readonly = True

    def url(self, *args):
        """return url for the controller and add args to path"""
        u = url(controller=self.plural)
        if args:
            u += '/' + '/'.join([str(a) for a in args])
        return u

    def index(self, format='html'):
        page = self.get_page()
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

    def create(self, format='html'):
        fs = self.get_add_fieldset()
        if format == 'json':
            data = request.POST.copy()
            request.body = ''
            if hasattr(fs, 'model'):
                # this should bread if fs is a non standard fieldset
                name = '%s-' % fs.model.__class__.__name__
                for k, v in data.items():
                    if not k.startswith(name):
                        if isinstance(v, list):
                            for val in v:
                                request.POST.add('%s-%s' % (name, k), str(val))
                        else:
                            request.POST.add('%s-%s' % (name, k), str(v))
        else:
            data = request.POST

        fs = fs.bind(fs.model, data=request.POST, session=self.Session())
        if fs.validate():
            fs.sync()
            self.sync(fs)
            if format == 'html':
                redirect_to(self.url())
            else:
                return self.render_json(fs=fs)
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

    def new(self, id, format='html'):
        fs = self.get_add_fieldset()
        fs = fs.bind(session=self.Session())
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

