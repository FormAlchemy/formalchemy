# standard pylons controller imports
import os
import logging
log = logging.getLogger(__name__)

from pylons import request, response, session, config
from pylons import tmpl_context as c

from pylons import url
from pylons.controllers.util import redirect_to
import pylons.controllers.util as h
from webhelpers.paginate import Page

from sqlalchemy.orm import class_mapper, object_session
from formalchemy import *
from formalchemy.i18n import _, get_translator
from formalchemy.fields import _pk
from formalchemy.templates import MakoEngine


__all__ = ['FormAlchemyAdminController']

# misc labels
_('Edit')
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

def flash(msg):
    """Add 'msg' to the users flashest list in the users session"""
    flashes = session.setdefault('_admin_flashes', [])
    flashes.append(msg)
    session.save()


def get_forms(controller, model_module, forms):
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
        def get_linker(action, modelname=modelname):
            _ = get_translator().gettext
            label = action == 'edit' and _('edit') or _('delete')
            return lambda item: '<a href="%s" title="%s" class="icon %s">%s</a>' % (
                                url(controller=controller,
                                          modelname=modelname,
                                          action=action,
                                          id=_pk(item)),
                                label,
                                action,
                                label)
        for action in ['edit', 'delete']:
            grid.append(Field(action, types.String, get_linker(action)))
        grid.readonly = True

    return {'_model_fieldsets':model_fieldsets, '_model_grids':model_grids}


class AdminController(object):
    """Base class to generate administration interface in Pylons"""
    _custom_css = _custom_js = ''

    def index(self):
        """List model types"""
        modelnames = sorted(self._model_grids.keys())
        return self._engine('admin_index', c=c, modelname=None,
                                     controller=self._name,
                                     modelnames=modelnames,
                                     custom_css = self._custom_css,
                                     custom_js = self._custom_js)

    def list(self, modelname):
        """List instances of a model type"""
        grid = self._model_grids[modelname]
        S = self.Session()
        query = S.query(grid.model.__class__)
        page = Page(query, page=int(request.GET.get('page', '1')), **self._paginate)
        c.grid = grid.bind(page)
        c.modelname = modelname
        return self._engine('admin_list', c=c,
                            page=page,
                            controller=self._name,
                            modelname=modelname,
                            custom_css = self._custom_css,
                            custom_js = self._custom_js)

    def edit(self, modelname, id=None):
        """Edit (or create, if `id` is None) an instance of the given model type"""
        F_ = get_translator().gettext
        fs = self._model_fieldsets[modelname]
        S = self.Session()
        if id:
            instance = S.query(fs.model.__class__).get(id)
            c.fs = fs.bind(instance)
            title = 'Edit'
        else:
            c.fs = fs.bind(fs.model.__class__, session=S)
            title = 'New object'
        if request.method == 'POST':
            c.fs = c.fs.bind(data=request.params, session=not id and S or None)
            log.debug('saving %s w/ %s' % (c.fs.model.id, request.POST))
            if c.fs.validate():
                c.fs.sync()
                S.flush()
                if not id:
                    # needed if the object does not exist in db
                    if not object_session(c.fs.model):
                        S.save(c.fs.model)
                    message = _('Created %s %s')
                else:
                    S.refresh(c.fs.model)
                    message = _('Modified %s %s')
                S.commit()
                message = F_(message) % (modelname.encode('utf-8', 'ignore'),
                                         _pk(c.fs.model))
                flash(message)
                redirect_to(url(controller=self._name,
                                modelname=modelname, action='list'))
        return self._engine('admin_edit', c=c,
                                    action=title, id=id,
                                    controller=self._name,
                                    modelname=modelname,
                                    custom_css = self._custom_css,
                                    custom_js = self._custom_js)

    def delete(self, modelname, id):
        """Delete an instance of the given model type"""
        F_ = get_translator().gettext
        fs = self._model_fieldsets[modelname]
        S = self.Session()
        instance = S.query(fs.model.__class__).get(id)
        key = _pk(instance)
        S.delete(instance)
        S.commit()
        message = F_(_('Deleted %s %s')) % (modelname.encode('utf-8', 'ignore'),
                                            key)
        flash(message)
        redirect_to(url(controller=self._name, modelname=modelname, action='list'))

    def static(self, id):
        filename = os.path.basename(id)
        if filename not in os.listdir(template_dir):
            raise IOError('Invalid filename: %s' % filename)
        filepath = os.path.join(template_dir, filename)
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

def FormAlchemyAdminController(cls, engine=None, controller=None,
                               paginate=dict()):
    """
    Generate a controller that is a subclass of `AdminController`
    and the Pylons BaseController `cls`
    """
    if not controller:
        controller = cls.__name__.lower().split('controller')[0]

    kwargs = get_forms(controller, cls.model, cls.forms)
    log.info('creating admin controller with args %s' % kwargs)

    kwargs['_name'] = controller
    kwargs['_paginate'] = paginate
    if engine is not None:
        kwargs['_engine'] = engine
    else:
        kwargs['_engine'] = TemplateEngine(input_encoding='utf-8', output_encoding='utf-8')

    return type(cls.__name__, (cls, AdminController), kwargs)
