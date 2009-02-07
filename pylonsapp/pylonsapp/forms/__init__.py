from pylonsapp import model
from pylonsapp.lib.base import render
from formalchemy import validators
from formalchemy import fields
from formalchemy import forms
from formalchemy import tables

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

