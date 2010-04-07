# Copyright (C) 2007 Alexandre Conrad, alexandre (dot) conrad (at) gmail (dot) com
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import warnings
import logging
logger = logging.getLogger('formalchemy.' + __name__)

import base, fields
from validators import ValidationError
from formalchemy import config
from formalchemy import exceptions

from tempita import Template as TempitaTemplate # must import after base


__all__ = ['AbstractFieldSet', 'FieldSet', 'form_data']


def form_data(fieldset, params):
    """
    deprecated.  moved the "pull stuff out of a request object" stuff
    into relevant_data().  until this is removed it is a no-op.
    """
    return params


class AbstractFieldSet(base.EditableRenderer):
    """
    `FieldSets` are responsible for generating HTML fields from a given
    `model`.

    You can derive your own subclasses from `FieldSet` or `AbstractFieldSet`
    to provide a customized `render` and/or `configure`.

    `AbstractBaseSet` encorporates validation/errors logic and provides a default
    `configure` method.  It does *not* provide `render`.

    You can write `render` by manually sticking strings together if that's what you want,
    but we recommend using a templating package for clarity and maintainability.
    !FormAlchemy includes the Tempita templating package as formalchemy.tempita;
    see http://pythonpaste.org/tempita/ for documentation.

    `formalchemy.forms.template_text_tempita` is the default template used by `FieldSet.`
    !FormAlchemy also includes a Mako version, `formalchemy.forms.template_text_mako`,
    and will use that instead if Mako is available.  The rendered HTML is identical
    but (we suspect) Mako is faster.
    """
    def __init__(self, *args, **kwargs):
        base.EditableRenderer.__init__(self, *args, **kwargs)
        self.validator = None
        self._errors = []

    def configure(self, pk=False, exclude=[], include=[], options=[], global_validator=None):
        """
        `global_validator` should be a function that performs validations that need
        to know about the entire form.  The other parameters are passed directly
        to `ModelRenderer.configure`.

        - `pk=False`:
              set to True to include primary key columns

        - `exclude=[]`:
              an iterable of attributes to exclude.  Other attributes will
              be rendered normally

        - `include=[]`:
              an iterable of attributes to include.  Other attributes will
              not be rendered

        - `options=[]`:
              an iterable of modified attributes.  The set of attributes to
              be rendered is unaffected

        - `global_validator=None`:
              `global_validator` should be a function that performs
              validations that need to know about the entire form.

        Only one of {`include`, `exclude`} may be specified.

        Note that there is no option to include foreign keys.  This is
        deliberate.  Use `include` if you really need to manually edit FKs.

        If `include` is specified, fields will be rendered in the order given
        in `include`.  Otherwise, fields will be rendered in order of declaration,
        with table fields before mapped properties.  (However, mapped property order
        is sometimes ambiguous, e.g. when backref is involved.  In these cases,
        FormAlchemy will take its best guess, but you may have to force the
        "right" order with `include`.)

        """
        base.EditableRenderer.configure(self, pk, exclude, include, options)
        self.validator = global_validator

    def validate(self):
        """
        Validate attributes and `global_validator`.
        If validation fails, the validator should raise `ValidationError`.
        """
        if self.data is None:
            raise Exception('Cannot validate without binding data')
        success = True
        for field in self.render_fields.itervalues():
            success = field._validate() and success
        # run this _after_ the field validators, since each field validator
        # resets its error list. we want to allow the global validator to add
        # errors to individual fields.
        if self.validator:
            self._errors = []
            try:
                self.validator(self)
            except ValidationError, e:
                self._errors = e.args
                success = False
        return success

    @property
    def errors(self):
        """
        A dictionary of validation failures.  Always empty before `validate()` is run.
        Dictionary keys are attributes; values are lists of messages given to `ValidationError`.
        Global errors (not specific to a single attribute) are under the key `None`.
        """
        errors = {}
        if self._errors:
            errors[None] = self._errors
        errors.update(dict([(field, field.errors)
                            for field in self.render_fields.itervalues() if field.errors]))
        return errors

    def __repr__(self):
        _fields = self._fields
        conf = ''
        if self._render_fields:
            conf = ' (configured)'
            _fields = self._render_fields
        return '<%s%s with %r>' % (self.__class__.__name__, conf,
                                   _fields.keys())


class FieldSet(AbstractFieldSet):
    """
    A `FieldSet` is bound to a SQLAlchemy mapped instance (or class, for
    creating new instances) and can render a form for editing that instance,
    perform validation, and sync the form data back to the bound instance.

    """
    engine = _render = _render_readonly = None

    def __init__(self, *args, **kwargs):
        AbstractFieldSet.__init__(self, *args, **kwargs)
        self.focus = True
        self.readonly = False

    def configure(self, pk=False, exclude=[], include=[], options=[], global_validator=None, focus=True, readonly=False):
        """
        Besides the options in :meth:`AbstractFieldSet.configure`,
        `FieldSet.configure` takes the `focus` parameter, which should be the
        attribute (e.g., `fs.orders`) whose rendered input element gets focus. Default value is
        True, meaning, focus the first element. False means do not focus at
        all.

        This `configure` adds two parameters:

        - `focus=True`:
              the attribute (e.g., `fs.orders`) whose rendered input element
              gets focus. Default value is True, meaning, focus the first
              element. False means do not focus at all.

        - `readonly=False`:
              if true, the fieldset will be rendered as a table (tbody)
              instead of a group of input elements.  Opening and closing
              table tags are not included.


        """
        AbstractFieldSet.configure(self, pk, exclude, include, options, global_validator)
        self.focus = focus
        self.readonly = readonly

    def validate(self):
        if self.readonly:
            raise Exception('Cannot validate a read-only FieldSet')
        return AbstractFieldSet.validate(self)

    def sync(self):
        if self.readonly:
            raise Exception('Cannot sync a read-only FieldSet')
        AbstractFieldSet.sync(self)

    def render(self, **kwargs):
        if fields._pk(self.model) != self._bound_pk and self.data is not None:
            msg = ("Primary key of model has changed since binding, "
                   "probably due to sync()ing a new instance (from %r to %r). "
                   "You can solve this by either binding to a model "
                   "with the original primary key again, or by binding data to None.")
            raise exceptions.PkError(msg % (self._bound_pk, fields._pk(self.model)))
        engine = self.engine or config.engine
        if self._render or self._render_readonly:
            warnings.warn(DeprecationWarning('_render and _render_readonly are deprecated and will be removed in 1.5. Use a TemplateEngine instead'))
        if self.readonly:
            if self._render_readonly is not None:
                engine._update_args(kwargs)
                return self._render_readonly(fieldset=self, **kwargs)
            return engine('fieldset_readonly', fieldset=self, **kwargs)
        if self._render is not None:
            engine._update_args(kwargs)
            return self._render(fieldset=self, **kwargs)
        return engine('fieldset', fieldset=self, **kwargs)
