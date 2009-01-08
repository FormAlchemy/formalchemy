# standard pylons controller imports
import os
import logging
log = logging.getLogger(__name__)

from pylons import request, response, session
try:
    from pylons import tmpl_context as c
except:
    from pylons import c
from pylons.controllers.util import redirect_to, url_for
import pylons.controllers.util as h

from sqlalchemy.orm import class_mapper
from formalchemy import *
from formalchemy.i18n import _, get_translator
from formalchemy.fields import _pk
from formalchemy.tempita import Template


__all__ = ['FormAlchemyAdminController']

# misc labels
_('Edit')
_('Delete')
_('Cancel')

# templates

template_dir = os.path.dirname(__file__)

def load_text(filename):
    fd = open(os.path.join(template_dir, '%s.tmpl' % filename))
    data = fd.read()
    fd.close()
    return data

def load_template(filename):
    flash = load_text('admin_flash')
    body = load_text(filename)
    html = """<html>
{{py:
from pylons.controllers.util import url_for
_ = F_
}}
<head>
<style media="screen" type="text/css"><!-- @import url({{url_for(modelname='static_contents', action='admin.css', id=None)}}); --></style>
%(flash)s
{{custom_css}}
{{custom_js}}
</head>
{{if modelname:}}
<div>
  <a href="{{url_for(modelname=None, action=None, id=None)}}">
    &lt;&lt; {{F_('Models')}}
  </a>
</div>
{{endif}}
%(body)s
</html>
""" % locals()
    return Template(html)

index_template = load_template('admin_index')
list_template = load_template('admin_list')
edit_template = load_template('admin_edit')


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
            return lambda item: '<a href="%s">%s</a>' % (
                                h.url_for(modelname=modelname,
                                action=action,
                                id=_pk(item)),
                                get_translator().gettext(action))
        old_include = grid.render_fields.values() # grab this now, or .add will change it if user didn't call configure yet
        for action in ['edit', 'delete']:
            grid.add(Field(action, types.String, get_linker(action)))
        grid.configure(include=old_include + [grid.edit, grid.delete], readonly=True)

    return {'_model_fieldsets':model_fieldsets, '_model_grids':model_grids}


class AdminController(object):
    """Base class to generate administration interface in Pylons"""
    _custom_css = _custom_js = ''

    def index(self):
        """List model types"""
        F_ = get_translator().gettext
        modelnames = sorted(self._model_grids.keys())
        return index_template.substitute(c=c, h=h, F_=F_,
                                         modelname=None,
                                         modelnames=modelnames,
                                         custom_css = self._custom_css,
                                         custom_js = self._custom_js)

    def list(self, modelname):
        """List instances of a model type"""
        F_ = get_translator().gettext
        grid = self._model_grids[modelname]
        S = self.Session()
        instances = S.query(grid.model.__class__).all()
        c.grid = grid.bind(instances)
        c.modelname = modelname
        return list_template.substitute(c=c, h=h, F_=F_,
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
            c.fs = c.fs.bind(data=request.params)
            log.debug('saving %s w/ %s' % (c.fs.model.id, request.POST))
            if c.fs.validate():
                c.fs.sync()
                S.flush()
                if not id:
                    # needed if the object does not exist in db
                    S.save(c.fs.model)
                    message = _('Created %s %s')
                else:
                    S.refresh(c.fs.model)
                    message = _('Modified %s %s')
                S.commit()
                message = F_(message) % (modelname.encode('utf-8', 'ignore'),
                                         _pk(c.fs.model))
                flash(message)
                redirect_to(url_for(modelname=modelname,
                                    action='list', id=None))
        return edit_template.substitute(c=c, h=h, F_=F_,
                                        title=title, id=id,
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
        redirect_to(url_for(modelname=modelname, action='list', id=None))

    def static(self, id):
        filename = os.path.basename(id)
        if filename not in os.listdir(template_dir):
            raise IOError('Invalid filename: %s' % filename)
        filepath = os.path.join(template_dir, filename)
        if filename.endswith('.css'):
            response.headers['Content-type'] = "text/css"
        elif filename.endswith('.js'):
            response.headers['Content-type'] = "text/javascript"
        else:
            raise IOError('Invalid filename: %s' % filename)
        fd = open(filepath)
        data = fd.read()
        fd.close()
        return data

def FormAlchemyAdminController(cls):
    """
    Generate a controller that is a subclass of `AdminController`
    and the Pylons BaseController `cls`
    """
    controller = cls.__name__.lower().split('controller')[0]
    kwargs = get_forms(controller, cls.model, cls.forms)
    log.info('creating admin controller with args %s' % kwargs)
    return type(cls.__name__, (cls, AdminController), kwargs)
