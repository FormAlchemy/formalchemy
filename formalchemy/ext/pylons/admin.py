# standard pylons controller imports
import os
import logging
log = logging.getLogger(__name__)

from pylons import request, response, session, config
from pylons import tmpl_context as c

from pylons import url
from pylons.controllers.util import redirect
import pylons.controllers.util as h
from webhelpers.paginate import Page

from sqlalchemy.orm import class_mapper, object_session
from formalchemy import *
from formalchemy.i18n import _, get_translator
from formalchemy.fields import _pk
from formalchemy.templates import MakoEngine

import simplejson as json

__all__ = ['FormAlchemyAdminController']

# misc labels
_('Add')
_('Edit')
_('New')
_('Save')
_('Delete')
_('Cancel')
_('Models')
_('Existing objects')
_('New object')
_('Related types')
_('Existing objects')
_('Create form')

# templates

template_dir = os.path.dirname(__file__)
static_dir = os.path.join(template_dir, 'resources')

def flash(msg):
    """Add 'msg' to the users flashest list in the users session"""
    flashes = session.setdefault('_admin_flashes', [])
    flashes.append(msg)
    session.save()


def get_forms(model_module, forms):
    """scan model and forms"""
    if forms is not None:
        model_fieldsets = dict((form.model.__class__.__name__, form)
                               for form in forms.__dict__.itervalues()
                               if isinstance(form, FieldSet))
        model_grids = dict((form.model.__class__.__name__, form)
                           for form in forms.__dict__.itervalues()
                           if isinstance(form, Grid))
    else:
        model_fieldsets = dict()
        model_grids = dict()

    # generate missing forms, grids
    for key, obj in model_module.__dict__.iteritems():
        try:
            class_mapper(obj)
        except:
            continue
        if not isinstance(obj, type):
            continue
        if key not in model_fieldsets:
            model_fieldsets[key] = FieldSet(obj)
        if key not in model_grids:
            model_grids[key] = Grid(obj)
    # add Edit + Delete link to grids
    for modelname, grid in model_grids.iteritems():
        def edit_link():
            model_url = url('models', modelname=modelname)
            return lambda item: '<a href="%(url)s/%(id)s" title="%(label)s" class="icon edit">%(label)s</a>' % dict(
                                url=model_url, id=_pk(item),
                                label=get_translator().gettext('edit'))
        def delete_link():
            model_url = url('models', modelname=modelname)
            return lambda item: '''<form action="%(url)s/%(id)s" method="POST">
                                    <input type="submit" class="icon delete" title="%(label)s" value="" />
                                    <input type="hidden" name="_method" value="DELETE" />
                                    </form>
                                ''' % dict(
                                    url=model_url, id=_pk(item),
                                    label=get_translator().gettext('delete'))
        grid.append(Field('edit', types.String, edit_link()))
        grid.append(Field('delete', types.String, delete_link()))
        grid.readonly = True

    return {'_model_fieldsets':model_fieldsets, '_model_grids':model_grids}


class AdminController(object):
    """Base class to generate administration interface in Pylons"""
    _custom_css = _custom_js = ''

    def render_json(self, fs=None, **kwargs):
        response.content_type = 'text/javascript'
        if fs:
            fields = dict([(field.key, field.model_value) for field in fs.render_fields.values()])
            data = dict(fields=fields)
            pk = _pk(fs.model)
            if pk:
                data['url'] = url('view_model', modelname=fs.model.__class__.__name__, id=pk)
        else:
            data = {}
        data.update(kwargs)
        return json.dumps(data)

    def index(self, format='html'):
        """List model types"""
        modelnames = sorted(self._model_grids.keys())
        if format == 'json':
            return self.render_json(**dict([(m, url('models', modelname=m)) for m in modelnames]))
        return self._engine('admin_index', c=c, modelname=None,
                                     modelnames=modelnames,
                                     custom_css = self._custom_css,
                                     custom_js = self._custom_js)

    def list(self, modelname, format='html'):
        """List instances of a model type"""
        S = self.Session()
        grid = self._model_grids[modelname]
        query = S.query(grid.model.__class__)
        page = Page(query, page=int(request.GET.get('page', '1')), **self._paginate)
        if format == 'json':
            values = []
            for item in page:
                pk = _pk(item)
                values.append((pk, url('view_model', pk)))
            return self.render_json(records=dict(values), page_count=page.page_count, page=page.page)
        grid = grid.bind(instances=page, session=None)
        clsnames = [f.relation_type().__name__ for f in grid._fields.itervalues() if f.is_relation]
        return self._engine('admin_list', c=c,
                            grid=grid,
                            page=page,
                            clsnames=clsnames,
                            modelname=modelname,
                            custom_css = self._custom_css,
                            custom_js = self._custom_js)

    def edit(self, modelname, id=None, format='html'):
        """Edit (or create, if `id` is None) an instance of the given model type"""

        saved = 1

        if id and id.endswith('.json'):
            id = id[:-5]
            format = 'json'

        if request.method == 'POST' or format == 'json':
            if id:
                prefix = '%s-%s' % (modelname, id)
            else:
                prefix = '%s-' % modelname

            if request.method == 'PUT':
                items = json.load(request.body_file).items()
                request.method = 'POST'
            elif '_method' not in request.POST:
                items = request.POST.items()
                format = 'json'
            else:
                items = None

            if items:
                for k, v in items:
                    if not k.startswith(prefix):
                        if isinstance(v, list):
                            for val in v:
                                request.POST.add('%s-%s' % (prefix, k), val)
                        else:
                            request.POST.add('%s-%s' % (prefix, k), v)

        fs = self._model_fieldsets[modelname]
        S = self.Session()

        if id:
            instance = S.query(fs.model.__class__).get(id)
            assert instance, id
            title = 'Edit'
        else:
            instance = fs.model.__class__
            title = 'New object'

        if request.method == 'POST':
            F_ = get_translator().gettext
            c.fs = fs.bind(instance, data=request.POST, session=not id and S or None)
            if c.fs.validate():
                c.fs.sync()
                S.flush()
                if not id:
                    # needed if the object does not exist in db
                    if not object_session(c.fs.model):
                        S.add(c.fs.model)
                    message = _('Created %s %s')
                else:
                    S.refresh(c.fs.model)
                    message = _('Modified %s %s')
                S.commit()
                saved = 0

                if format == 'html':
                    message = F_(message) % (modelname.encode('utf-8', 'ignore'),
                                             _pk(c.fs.model))
                    flash(message)
                    redirect(url('models', modelname=modelname))
        else:
            c.fs = fs.bind(instance, session=not id and S or None)

        if format == 'html':
            return self._engine('admin_edit', c=c,
                                        action=title, id=id,
                                        modelname=modelname,
                                        custom_css = self._custom_css,
                                        custom_js = self._custom_js)
        else:
            return self.render_json(fs=c.fs, status=saved, model=modelname)

    def delete(self, modelname, id, format='html'):
        """Delete an instance of the given model type"""
        F_ = get_translator().gettext
        fs = self._model_fieldsets[modelname]
        S = self.Session()
        instance = S.query(fs.model.__class__).get(id)
        key = _pk(instance)
        S.delete(instance)
        S.commit()

        if format == 'html':
            message = F_(_('Deleted %s %s')) % (modelname.encode('utf-8', 'ignore'),
                                                key)
            flash(message)
            redirect(url('models', modelname=modelname))
        else:
            return self.render_json(status=0)

    def static(self, id):
        filename = os.path.basename(id)
        if filename not in os.listdir(static_dir):
            raise IOError('Invalid filename: %s' % filename)
        filepath = os.path.join(static_dir, filename)
        if filename.endswith('.css'):
            response.headers['Content-type'] = "text/css"
        elif filename.endswith('.js'):
            response.headers['Content-type'] = "text/javascript"
        elif filename.endswith('.png'):
            response.headers['Content-type'] = "image/png"
        else:
            raise IOError('Invalid filename: %s' % filename)
        fd = open(filepath, 'rb')
        data = fd.read()
        fd.close()
        return data

class TemplateEngine(MakoEngine):
    directories = [os.path.join(p, 'fa_admin') for p in config['pylons.paths']['templates']] + [template_dir]
    _templates = ['base', 'admin_index', 'admin_list', 'admin_edit']

def FormAlchemyAdminController(cls, engine=None, paginate=dict(), **kwargs):
    """
    Generate a controller that is a subclass of `AdminController`
    and the Pylons BaseController `cls`
    """
    kwargs = get_forms(cls.model, cls.forms)
    log.info('creating admin controller with args %s' % kwargs)

    kwargs['_paginate'] = paginate
    if engine is not None:
        kwargs['_engine'] = engine
    else:
        kwargs['_engine'] = TemplateEngine(input_encoding='utf-8', output_encoding='utf-8')

    return type(cls.__name__, (cls, AdminController), kwargs)
