from pylons import config
from pylonsapp import model
from pylonsapp.lib.base import render
from formalchemy import validators
from formalchemy import fields
from formalchemy import forms
from formalchemy import tables
from formalchemy.ext.fsblob import FileFieldRenderer
from formalchemy.ext.fsblob import ImageFieldRenderer

if 'storage_path' in config['app_conf']:
    # set the storage_path if we can find an options in app_conf
    FileFieldRenderer.storage_path = config['app_conf']['storage_path']
    ImageFieldRenderer.storage_path = config['app_conf']['storage_path']

class FieldSet(forms.FieldSet):
    def _render(self, **kwargs):
        return render('/fieldset.mako',
                      extra_vars=kwargs)
    def _render_readonly(self, **kwargs):
        return render('/fieldset_readonly.mako',
                      extra_vars=kwargs)

class Grid(tables.Grid):
    def _render(self, **kwargs):
        return render('/grid.mako',
                      extra_vars=kwargs)
    def _render_readonly(self, **kwargs):
        return render('/grid_readonly.mako',
                      extra_vars=kwargs)

## Initialize fieldsets

#Foo = FieldSet(model.Foo)
#Reflected = FieldSet(Reflected)

## Initialize grids

#FooGrid = Grid(model.Foo)
#ReflectedGrid = Grid(Reflected)

