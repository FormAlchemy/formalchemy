from {{package}} import model
from {{package}}.lib.base import render
from formalchemy import validators
from formalchemy import fields
{{if template_engine == 'mako'}}
from formalchemy import forms
from formalchemy import tables

class FieldSet(forms.FieldSet):
    def _render(self, **kwargs):
        return render('/fieldset.mako')
    def _render_readonly(self, **kwargs):
        return render('/fieldset_readonly.mako')

class Grid(tables.Grid):
    def _render(self, **kwargs):
        return render('/grid.mako')
    def _render_readonly(self, **kwargs):
        return render('/grid_readonly.mako')
{{else}}
from formalchemy.forms import FieldSet
from formalchemy.tables import Grid
{{endif}}

## Initialize fieldsets

#Foo = FieldSet(model.Foo)
#Reflected = FieldSet(Reflected)

## Initialize grids

#FooGrid = Grid(model.Foo)
#ReflectedGrid = Grid(Reflected)

