# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import helpers as h

import base

from tempita import Template as TempitaTemplate # must import after base


__all__ = ["Grid"]


template_grid_readonly = r"""
<thead>
  <tr>
    {{for field in collection.render_fields.itervalues()}}
      <th>{{field.label_text or collection.prettify(field.key)}}</td>
    {{endfor}}
  </tr>
</thead>

<tbody>
{{for row in collection.rows:}}
  {{collection._set_active(row)}}
  <tr>
  {{for field in collection.render_fields.itervalues()}}
    <td>{{field.render_readonly()}}</td>
  {{endfor}}
  </tr>
{{endfor}}
</tbody>
"""
render_grid_readonly = TempitaTemplate(template_grid_readonly, name='template_grid_readonly').substitute

template_grid = r"""
<thead>
  <tr>
    {{for field in collection.render_fields.itervalues()}}
      <th>{{field.label_text or collection.prettify(field.key)}}</td>
    {{endfor}}
  </tr>
</thead>

<tbody>
{{for row in collection.rows:}}
  {{collection._set_active(row)}}
  <tr>
  {{for field in collection.render_fields.itervalues()}}
    <td>
      {{field.render()}}
      {{for error in field.errors}}
      <span class="grid_error">{{error}}</span>
      {{endfor}}
    </td>
  {{endfor}}
  </tr>
{{endfor}}
</tbody>
"""
render_grid = TempitaTemplate(template_grid, name='template_grid').substitute


def _validate_iterable(o):
    try:
        iter(o)
    except:
        raise Exception('instances must be an iterable, not %s' % o)


class Grid(base.EditableRenderer):
    """
    Besides `FieldSet`, `FormAlchemy` provides `Grid` for editing and
    rendering multiple instances at once.  Most of what you know about
    `FieldSet` applies to `Grid`, with the following differences to
    accomodate being bound to multiple objects:

    The `Grid` constructor takes the following arguments:

    * `cls`: the class type that the `Grid` will render (NOT an instance)

    * `instances=[]`: the instances/rows to render

    * `session=None`: as in `FieldSet`

    * `data=None`: as in `FieldSet`

    `bind` and `rebind` take the last 3 arguments (`instances`, `session`,
    and `data`); you may not specify a different class type than the one
    given to the constructor.

    The `Grid` `errors` attribute is a dictionary keyed by bound instance,
    whose value is similar to the `errors` from a `FieldSet`, that is, a
    dictionary whose keys are `Field`s, and whose values are
    `ValidationError` instances.
    """
    _render = staticmethod(render_grid)
    _render_readonly = staticmethod(render_grid_readonly)

    def __init__(self, cls, instances=[], session=None, data=None):
        from sqlalchemy.orm import class_mapper
        if not class_mapper(cls):
            raise Exception('Grid must be bound to an SA mapped class')
        base.EditableRenderer.__init__(self, cls, session, data)
        self.rows = instances
        self.readonly = False
        self.errors = {}

    def configure(self, pk=False, exclude=[], include=[], options=[], readonly=False):
        """
        The `Grid` `configure` method takes the same arguments as `FieldSet`
        (`pk`, `exclude`, `include`, `options`, `readonly`), except there is
        no `focus` argument.
        """
        base.EditableRenderer.configure(self, pk, exclude, include, options)
        self.readonly = readonly

    def bind(self, instances, session=None, data=None):
        """bind to instances"""
        _validate_iterable(instances)
        if not session:
            i = iter(instances)
            try:
                instance = i.next()
            except StopIteration:
                pass
            else:
                from sqlalchemy.orm import object_session
                session = object_session(instance)
        mr = base.EditableRenderer.bind(self, self.model, session, data)
        mr.rows = instances
        return mr

    def rebind(self, instances=None, session=None, data=None):
        """rebind to instances"""
        if instances is not None:
            _validate_iterable(instances)
        base.EditableRenderer.rebind(self, self.model, session, data)
        if instances is not None:
            self.rows = instances

    def render(self, **kwargs):
        if self.readonly:
            return self._render_readonly(collection=self, **kwargs)
        return self._render(collection=self, **kwargs)

    def _set_active(self, instance, session=None):
        base.EditableRenderer.rebind(self, instance, session or self.session, self.data)

    def validate(self):
        """These are the same as in `FieldSet`"""
        if self.data is None:
            raise Exception('Cannot validate without binding data')
        if self.readonly:
            raise Exception('Cannot validate a read-only Grid')
        self.errors.clear()
        success = True
        for row in self.rows:
            self._set_active(row)
            row_errors = {}
            for field in self.render_fields.itervalues():
                success = field._validate() and success
                if field.errors:
                    row_errors[field] = field.errors
            self.errors[row] = row_errors
        return success

    def sync_one(self, row):
        """
        Use to sync a single one of the instances that are
        bound to the `Grid`.
        """
        # we want to allow the user to sync just rows w/o errors, so this is public
        if self.readonly:
            raise Exception('Cannot sync a read-only Grid')
        self._set_active(row)
        base.EditableRenderer.sync(self)

    def sync(self):
        """These are the same as in `FieldSet`"""
        for row in self.rows:
            self.sync_one(row)
