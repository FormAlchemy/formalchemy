# -*- coding: utf-8 -*-
__doc__ = """This module provide a RESTful controller for formalchemy's FieldSets.
"""
from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons.templating import render_mako as render
from pylons import url
from webhelpers.paginate import Page
from sqlalchemy.orm import class_mapper, object_session
from formalchemy.fields import _pk
from formalchemy import Grid, FieldSet
from formalchemy.i18n import get_translator
from formalchemy.fields import Field
from formalchemy import fatypes

import simplejson as json

def model_url(*args, **kwargs):
    if 'model_name' in request.environ['pylons.routes_dict']:
        kwargs['model_name'] = request.environ['pylons.routes_dict']['model_name']
    return url(*args, **kwargs)

class Session(object):
    def add(self, record):
        """add a record"""
    def update(self, record):
        """update a record"""
    def delete(self, record):
        """delete a record"""
    def commit(self):
        """commit transaction"""

class _RESTController(object):

    template = '/restfieldset.mako'
    engine = prefix_name = None
    pager_args = dict(link_attr={'class': 'ui-pager-link ui-state-default ui-corner-all'},
                      curpage_attr={'class': 'ui-pager-curpage ui-state-highlight ui-corner-all'})

    @property
    def model_name(self):
        """return ``model_name`` from ``pylons.routes_dict``"""
        return request.environ['pylons.routes_dict'].get('model_name', None)

    def Session(self):
        """return a Session object. You **must** override this."""
        return Session()

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

    def breadcrumb(self, action=None, fs=None, id=None, **kwargs):
        """return items to build the breadcrumb"""
        items = []
        if self.prefix_name:
            items.append((url(self.prefix_name), self.prefix_name))
        if self.model_name:
            items.append((model_url(self.collection_name), self.model_name))
        elif not self.prefix_name and 'is_grid' not in kwargs:
            items.append((model_url(self.collection_name), self.collection_name))
        if id and hasattr(fs.model, '__unicode__'):
            items.append((model_url(self.member_name, id=id), u'%s' % fs.model))
        elif id:
            items.append((model_url(self.member_name, id=id), id))
        if action in ('edit', 'new'):
            items.append((None, action))
        return items

    def render(self, format='html', **kwargs):
        """render the form as html or json"""
        if format == 'json':
            return self.render_json(**kwargs)
        kwargs.update(model_name=self.model_name or self.member_name,
                      prefix_name=self.prefix_name,
                      collection_name=self.collection_name,
                      member_name=self.member_name,
                      breadcrumb=self.breadcrumb(**kwargs))
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
            fs.engine = fs.engine or self.engine
            return fs
        """
        fs = FieldSet(self.get(id))
        fs.engine = fs.engine or self.engine
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
                ''' % dict(url=model_url('edit_%s' % self.member_name, id=_pk(item)),
                            label=get_translator().gettext('edit'))
            def delete_link():
                return lambda item: '''
                <form action="%(url)s" method="POST" class="ui-grid-icon ui-state-error ui-corner-all">
                <input type="submit" class="ui-icon ui-icon-circle-close" title="%(label)s" value="%(label)s" />
                <input type="hidden" name="_method" value="DELETE" />
                </form>
                ''' % dict(url=model_url(self.member_name, id=_pk(item)),
                           label=get_translator().gettext('delete'))
            grid.append(Field('edit', fatypes.String, edit_link()))
            grid.append(Field('delete', fatypes.String, delete_link()))
            grid.readonly = True

    def url(self, *args):
        """return url for the controller and add args to path"""
        u = model_url(self.collection_name)
        if args:
            u += '/' + '/'.join([str(a) for a in args])
        return u

    def index(self, format='html', **kwargs):
        page = self.get_page()
        if format == 'json':
            values = []
            for item in page:
                pk = _pk(item)
                value = hasattr(item, '__unicode__') and u'%s' % item or pk
                values.append(dict(pk=pk,
                                   url=model_url(self.member_name, id=pk),
                                   value=value))
            return self.render_json(records=values, page_count=page.page_count, page=page.page)
        fs = self.get_grid()
        fs = fs.bind(instances=page)
        fs.readonly = True
        return self.render_grid(format=format, fs=fs, id=None, pager=page.pager(**self.pager_args))

    def create(self, format='html', **kwargs):
        fs = self.get_add_fieldset()
        if format == 'json':
            data = request.POST.copy()
            request.body = ''
            #raise ValueError(data)
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
        return self.render(format=format, fs=fs, action='new', id=None)

    def delete(self, id, format='html', **kwargs):
        record = self.get(id)
        if record:
            S = self.Session()
            S.delete(record)
            S.commit()
        if format == 'html':
            redirect_to(self.url())
        return self.render_json(id=id)

    def show(self, id=None, format='html', **kwargs):
        fs = self.get_fieldset(id=id)
        fs.readonly = True
        return self.render(format=format, fs=fs, action='show', id=id)

    def new(self, format='html', **kwargs):
        fs = self.get_add_fieldset()
        fs = fs.bind(session=self.Session())
        action = self.url()
        return self.render(format=format, fs=fs, action='new', id=None)

    def edit(self, id=None, format='html', **kwargs):
        fs = self.get_fieldset(id)
        return self.render(format=format, fs=fs, action='edit', id=id)

    def update(self, id, format='html', **kwargs):
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
            return self.render(format=format, fs=fs, action='edit', id=id)
        else:
            return self.render(format=format, fs=fs, status=1)

def RESTController(cls, member_name, collection_name):
    """wrap a controller with :class:~formalchemy.ext.pylons.controller._RESTController"""
    return type(cls.__name__, (cls, _RESTController),
                dict(member_name=member_name, collection_name=collection_name))

class _ModelsController(_RESTController):

    engine = None
    model = forms = None

    def Session(self):
        return meta.Session

    def models(self, format='html', **kwargs):
        models = {}
        for key, obj in self.model.__dict__.iteritems():
            try:
                class_mapper(obj)
            except:
                continue
            if not isinstance(obj, type):
                continue
            models[key] = model_url(self.collection_name, model_name=key)
        return self.render(models=models, format=format)

    def get_model(self):
        if hasattr(self.model, self.model_name):
            return getattr(self.model, self.model_name)
        abort(404)

    def get_fieldset(self, id):
        if self.forms and hasattr(self.forms, self.model_name):
            fs = getattr(self.forms, self.model_name)
            fs.engine = fs.engine or self.engine
            return id and fs.bind(self.get(id)) or fs
        return _RESTController.get_fieldset(self, id)

    def get_add_fieldset(self):
        if self.forms and hasattr(self.forms, '%sAdd' % self.model_name):
            fs = getattr(self.forms, '%sAdd' % self.model_name)
            fs.engine = fs.engine or self.engine
            return fs
        return _RESTController.get_fieldset(self)

    def get_grid(self):
        model_name = self.model_name
        if self.forms and hasattr(self.forms, '%sGrid' % model_name):
            g = getattr(self.forms, '%sGrid' % model_name)
        if hasattr(self.model, model_name):
            model = getattr(self.model, model_name)
            g = Grid(model)
        else:
            abort(404)
        g.engine = g.engine or self.engine
        g.readonly = True
        self.update_grid(g)
        return g

def ModelsController(cls, prefix_name, member_name, collection_name):
    """wrap a controller with :class:~formalchemy.ext.pylons.controller._ModelsController"""
    return type(cls.__name__, (cls, _ModelsController),
                dict(prefix_name=prefix_name, member_name=member_name, collection_name=collection_name))

