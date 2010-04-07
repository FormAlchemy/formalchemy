# Copyright (C) 2007 Alexandre Conrad, alexandre (dot) conrad (at) gmail (dot) com
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import helpers as h

from formalchemy import config
from formalchemy import base

from tempita import Template as TempitaTemplate # must import after base


__all__ = ["Grid"]

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

    * `instances=[]`: the instances to render as grid rows

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
    engine = _render = _render_readonly = None

    def __init__(self, cls, instances=[], session=None, data=None, prefix=None):
        from sqlalchemy.orm import class_mapper
        if not class_mapper(cls):
            raise Exception('Grid must be bound to an SA mapped class')
        base.EditableRenderer.__init__(self, cls, session, data, prefix)
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
        engine = self.engine or config.engine
        if self._render or self._render_readonly:
            import warnings
            warnings.warn(DeprecationWarning('_render and _render_readonly are deprecated and will be removed in 1.5. Use a TemplateEngine instead'))
        if self.readonly:
            if self._render_readonly is not None:
                engine._update_args(kwargs)
                return self._render_readonly(collection=self, **kwargs)
            return engine('grid_readonly', collection=self, **kwargs)
        if self._render is not None:
            engine._update_args(kwargs)
            return self._render(collection=self, **kwargs)
        return engine('grid', collection=self, **kwargs)

    def _set_active(self, instance, session=None):
        base.EditableRenderer.rebind(self, instance, session or self.session, self.data)

    def get_errors(self, row):
        if self.errors:
            return self.errors.get(row, {})
        return {}

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
