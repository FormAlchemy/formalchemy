APP_NAME = 'contribtest' # set this to your application name

## LIMITATIONS
## normal FA restrictions (single PK, default constructor)
## must use Session.mapper (either w/ declarative or traditional table/class duology)

import logging
log = logging.getLogger(__name__)

from pylons import request, response, session
from pylons import tmpl_context as c
from pylons.controllers.util import redirect_to, url_for
import pylons.controllers.util as h

try:
    _basename = '%s.lib.base' % APP_NAME
    _base = __import__(_basename, fromlist=['%s.lib' % APP_NAME])
except ImportError:
    raise Exception('Invalid app name %s (unable to import %s)'
                    % (APP_NAME, _basename))
log.debug('imported base from ' + _base.__file__)
BaseController = _base.BaseController
render = _base.render

from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy.orm import class_mapper, object_session
from formalchemy import *
from formalchemy.fields import _pk
from mako.template import Template


# sort forms by type
model_module = __import__('%s.model' % APP_NAME, fromlist=[APP_NAME])
try:
    forms = __import__('%s.forms' % APP_NAME, fromlist=[APP_NAME])
except ImportError:
    class Empty(object): pass
    forms = Empty()
# dicts key off of strings rather than the model types themselves,
# because this makes it easier to just put the right string in the route.
model_fieldsets = dict((form.model.__class__.__name__, form)
                       for form in forms.__dict__.itervalues()
                       if isinstance(form, FieldSet))
model_grids = dict((form.model.__class__.__name__, form)
                   for form in forms.__dict__.itervalues()
                   if isinstance(form, Grid))
# generate missing forms, grids
for key, obj in model_module.__dict__.iteritems():
    try:
        class_mapper(obj)
    except UnmappedClassError:
        continue
    if not isinstance(obj, type):
        continue
    if key not in model_fieldsets:
        model_fieldsets[key] = FieldSet(obj)
    if key not in model_grids:
        model_grids[key] = Grid(obj)
# add Edit link to grids
for modelname, grid in model_grids.iteritems():
    def get_link(item, modelname=modelname):
        return '<a href="%s">edit</a>' % (h.url_for(controller='admin',
                                                  modelname=modelname,
                                                  action='details',
                                                  id=_pk(item)))
    old_include = grid.render_fields.values() # grab this now, or .add will change it if user didn't call configure yet
    grid.add(Field('edit', types.String, get_link))
    grid.configure(include=old_include + [grid.edit], readonly=True)

# templates
css = """
<style type="text/css">
.admin-flash {
    font-size:16pt; 
    font-weight: bold;
    background-color: #00FF00;
}

label {
    float: left;
    text-align: right;
    margin-right: 1em;
    width: 10em;
}

form div {
    margin: 0.5em;
    float: left;
    width: 100%;
}

form input[type="submit"] {
    margin-top: 1em;
    margin-left: 9em;
}

table {
  	border-collapse: collapse;
}

th, td {
    padding-left: 0.5em;
    padding-right: 0.5em;
}

th {
    background-color: #bbbbbb;
    border-bottom: 1px solid #8e8e8e;
    vertical-align: top;
}

</style>
"""

_flash_snippet = """
<%
 from pylons import session
 flashes = session.get('_admin_flashes', [])
 if flashes:
   session['_admin_flashes'] = []
   session.save()
%>
% for flash in flashes:
  <div class='admin-flash'>${flash}</div>
% endfor
"""

index_mako = """
<html>
  <head>
""" + css + _flash_snippet + """
  </head>
  <body>
    <h1>Models</h1>
    <ul>
    % for modelname in c.modelnames:
      <li><a href="${h.url_for(modelname=modelname, action="list")}">${modelname}</a></li>
    % endfor
    </ul>
  </body>
</html>
"""
index_template = Template(index_mako)

list_mako = """
<html>
  <head>
""" + css + _flash_snippet + """
  </head>
  <body>
    <h1>Related types</h1>
      <ul>
      % for field in c.grid._fields.itervalues():
        % if field.is_relation():
          <% clsname = field.relation_type().__name__ %>
          <li><a href="${h.url_for(modelname=clsname)}">${clsname}</a></li>
        % endif
      % endfor
      </ul>
    <h1>Existing objects</h1>
    <table>
      ${c.grid.render()}
    </table>
    <h1>New object</h1>
    <a href="${h.url_for(action='details')}">Create form</a>
  </body>
</html>
"""
list_template = Template(list_mako)

details_mako = """
<html>
  <head>
""" + css + _flash_snippet + """
  </head>
  <body>
    <form method="post">
      ${c.fs.render()}
      <input type="submit">
    </form>
  </body>
</html>
"""
details_template = Template(details_mako)


def flash(msg):
    """Add 'msg' to the users flashest list in the users session"""
    flashes = session.setdefault('_admin_flashes', [])
    flashes.append(msg)
    session.save()


def _class_session(model):
    # there isn't a clean way to get this from SA directly, so create an object
    # to throw away, just so we can get its session.
    instance = model()
    S = object_session(instance)
    S.expunge(instance)
    return S


class AdminController(BaseController):
    def index(self):
        c.modelnames = sorted(model_grids.keys())
        return index_template.render(c=c, h=h)

    def list(self, modelname):
        grid = model_grids[modelname]
        S = _class_session(grid.model.__class__)
        instances = S.query(grid.model.__class__).all()
        c.grid = grid.bind(instances)
        return list_template.render(c=c, h=h)

    def details(self, modelname, id=None):
        fs = model_fieldsets[modelname]
        S = _class_session(fs.model.__class__)
        if id:
            instance = S.query(fs.model.__class__).get(id)
            c.fs = fs.bind(instance)
        else:
            c.fs = fs.bind(fs.model.__class__)
        if request.method == 'POST':
            c.fs.rebind(c.fs.model, data=request.params)
            log.debug('saving %s w/ %s' % (c.fs.model.id, request.POST))
            if c.fs.validate():
                c.fs.sync()
                S.commit()
                flash(id == None and 'created' or 'modified')
                redirect_to(url_for(action='list'))
        return details_template.render(c=c, h=h)

    def delete(self, modelname, id):
        raise NotImplementedError()

# todo add logging
