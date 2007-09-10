# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import webhelpers as h
import sqlalchemy.types as types

import formalchemy.base as base
import formalchemy.fields as fields
import formalchemy.utils as utils

__all__ = ["FieldSet", "MultiFields", "Field"]

class FieldSet(base.BaseModelRender):
    """The `FieldSet` class.

    This class is responsible for generating HTML fieldsets from a given
    `model`.

    The one method to use is `render`. This is the method that returns
    generated HTML code from the `model` object.

    FormAlchemy has some default behaviour set. It is configured to generate
    the most HTML possible that will reflect the `model` object. Although,
    you can configure FormAlchemy to behave differently, thus altering the
    generated HTML output by many ways:

      * By passing keyword options to the `render` method:

        render(pk=False, fk=False, exclude=["private_column"])

      These options are NOT persistant. You'll need to pass these options
      everytime you call `render` or FormAlchemy will fallback to it's
      default behaviour. Passing keyword options is usually meant to alter
      the HTML output on the fly.

      * At the SQLAlchemy mapped class level, by creating a `FormAlchemy`
      subclass, it is possible to setup attributes which names and values
      correspond to the keyword options passed to `render`:

        class MyClass(object):
            class FormAlchemy:
                pk = False
                fk = False
                exclude = ["private_column"]

      These attributes are persistant and will be used as FormAlchemy's
      default behaviour.

      * By passing the keyword options to FormAlchemy's `configure` method.
      These options are persistant. and will be used as FormAlchemy's default
      behaviour.

        configure(pk=False, fk=False, exclude=["private_column"])

    Note: In any case, options set at the SQLAlchemy mapped class level or
    via the `configure` method will be overridden if these same keyword
    options are passed to `render`.

    """

    def render(self, **options):
        super(FieldSet, self).render()

        # Merge class level options with given argument options.
        opts = base.FormAlchemyDict(self.get_config())
        opts.configure(**options)

        model_render = MultiFields(self._model)
        # Reset options and only render based given options
        model_render.reconfigure(**opts)
        html = model_render.render()

        legend = opts.pop('legend', None)
        # Setup class's name as default.
        if legend is None:
            legend_txt = self._model.__class__.__name__
        # Don't render a legend field.
        elif legend is False:
            return utils.wrap("<fieldset>", html, "</fieldset>")
        # Use the user given string as the legend.
        elif isinstance(legend, basestring):
            legend_txt = legend

        html = "\n".join([h.content_tag('legend', legend_txt), html])
        return utils.wrap("<fieldset>", html, "</fieldset>")

class MultiFields(base.BaseModelRender):
    """The `MultiFields` class.

    Return generated HTML fields from a SQLAlchemy mapped class.

    """

    def render(self, **options):
        """Return HTML fields generated from the `model`."""

        super(MultiFields, self).render()

        # Merge class level options with given argument options.
        opts = base.FormAlchemyDict(self.get_config())
        opts.configure(**options)

        # Filter out unnecessary columns.
        columns = self.get_colnames(**opts)

        html = []
        # Generate fields.
        field_render = Field(bind=self._model)
        field_render.reconfigure(**opts)
        for col in columns:
            field_render.set_column(col)
            field = field_render.render()
            html.append(field)

        return "\n".join(html)

class Field(base.BaseColumnRender):
    """The `Field` class.

    Return generated HTML <label> and <input> tags for one single column.

    """

    def render(self, **options):
        super(Field, self).render()

        # Merge class level options with given argument options.
        opts = base.FormAlchemyDict(self.get_config())
        opts.configure(**options)

        # Categorize options
        readonlys = self.get_readonlys(**opts)

        passwords = opts.get('password', [])
        if isinstance(passwords, basestring):
            passwords = [passwords]
        hiddens = opts.get('hidden', [])
        if isinstance(hiddens, basestring):
            hiddens = [hiddens]
        dropdowns = opts.get('dropdown', {})
        radios = opts.get('radio', {})

        pretty_func = opts.get('prettify')
        aliases = opts.get('alias', {})

        errors = opts.get('error', {})
        docs = opts.get('doc', {})

        # Setup HTML classes
        cls_fld_req = opts.get('cls_req', 'field_req')
        cls_fld_opt = opts.get('cls_opt', 'field_opt')
        cls_fld_err = opts.get('cls_err', 'field_err')

        cls_span_doc = opts.get('span_doc', 'span_doc')
        cls_span_err = opts.get('span_err', 'span_err')

        # Process hidden fields first as they don't need a `Label`.
        if self._column in hiddens:
            return fields.HiddenField(self._model, self._column).render()

        # Make the label
        label = fields.Label(self._column, alias=aliases.get(self._column, self._column))
        label.set_prettify(pretty_func)
        if self.is_nullable(self._column):
            label.cls = cls_fld_opt
        else:
            label.cls = cls_fld_req
        field = label.render()

        # Hold a list of column names by type.
        col_types = self.get_coltypes()

        # Make the input
        if self._column in radios:
            radio = fields.RadioSet(self._model, self._column, choices=radios[self._column])
            field += "\n" + radio.render()

        elif self._column in dropdowns:
            dropdown = fields.SelectField(self._model, self._column, dropdowns[self._column].pop("opts"), **dropdowns[self._column])
            field += "\n" + dropdown.render()

        elif self._column in passwords:
            field += "\n" + fields.PasswordField(self._model, self._column, readonly=self._column in readonlys).render()

        elif self._column in col_types[types.String]:
            field += "\n" + fields.TextField(self._model, self._column).render()

        elif self._column in col_types[types.Integer]:
            field += "\n" + fields.IntegerField(self._model, self._column).render()

        elif self._column in col_types[types.Boolean]:
            field += "\n" + fields.BooleanField(self._model, self._column).render()

        elif self._column in col_types[types.DateTime]:
            field += "\n" + fields.DateTimeField(self._model, self._column).render()

        elif self._column in col_types[types.Date]:
            field += "\n" + fields.DateField(self._model, self._column).render()

        elif self._column in col_types[types.Time]:
            field += "\n" + fields.TimeField(self._model, self._column).render()

        elif self._column in col_types[types.Binary]:
            field += "\n" + fields.FileField(self._model, self._column).render()

        else:
            field += "\n" + fields.Field(self._model, self._column).render()

        # Make the error
        if self._column in errors:
            field += "\n" + h.content_tag("span", errors[self._column], class_=cls_span_err)
        # Make the documentation
        if self._column in docs:
            field += "\n" + h.content_tag("span", docs[self._column], class_=cls_span_doc)

        # Wrap the whole thing into a div
        field = utils.wrap("<div>", field, "</div>")

        return field
