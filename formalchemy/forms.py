# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import webhelpers as h
import sqlalchemy.types as types

import formalchemy.base as base
import formalchemy.fields as fields
import formalchemy.utils as utils

__all__ = ["FieldSet", "ModelRender", "FieldRender"]

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

        model_render = ModelRender(self._model)
        # Reset options and only render based given options
        model_render.reconfigure()
        html = model_render.render(**opts)

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

        html = h.content_tag('legend', legend_txt) + "\n" + html
        return utils.wrap("<fieldset>", html, "</fieldset>")

class ModelRender(base.BaseModelRender):
    """The `ModelRender` class.

    Return generated HTML fields from a SQLAlchemy mapped class.

    """

    def render(self, **options):
        """Return HTML fields generated from the `model`."""

        super(ModelRender, self).render()

        # Merge class level options with given argument options.
        opts = base.FormAlchemyDict(self.get_config())
        opts.configure(**options)

        # Filter out unnecessary columns.
        columns = self.get_colnames(**opts)

        html = []
        # Generate fields.
        field_render = FieldRender(bind=self._model)
        field_render.reconfigure()
        for col in columns:
            field_render.set_column(col)
            field = field_render.render(**opts)
            html.append(field)

        return "\n".join(html)

class FieldRender(base.BaseColumnRender):
    """The `FieldRender` class.

    Return generated HTML <label> and <input> tags for one single column.

    """

    def render(self, **options):
        super(FieldRender, self).render()

        # Merge class level options with given argument options.
        opts = base.FormAlchemyDict(self.get_config())
        opts.configure(**options)

        # Categorize options
        readonlys = self.get_readonlys(**opts)

        passwords = opts.get('password', [])
        hiddens = opts.get('hidden', [])
        dropdowns = opts.get('dropdown', {})
        radios = opts.get('radio', {})

        pretty_func = opts.get('prettify')
        aliases = opts.get('alias', {})

        errors = opts.get('error', {})
        docs = opts.get('doc', {})

        # Setup HTML classes
#        class_label = opts.get('cls_lab', 'form_label')
        class_required = opts.get('cls_req', 'field_req')
        class_optional = opts.get('cls_opt', 'field_opt')
        class_error = opts.get('cls_err', 'field_err')
        class_doc = opts.get('cls_doc', 'field_doc')

        # Process hidden fields first as they don't need a `Label`.
        if self._column in hiddens:
            return fields.HiddenField(self._model, col).render()

        # Make the label
        label = fields.Label(self._column, alias=aliases.get(self._column, self._column))
        label.set_prettify(pretty_func)
        if self.is_nullable(self._column):
            label.cls = class_optional
        else:
            label.cls = class_required
        field = label.render()

        # Hold a list of column names by type.
        col_types = self.get_coltypes()

        # Make the input
        if self._column in radios:
            radio = RadioSet(self._model, self._column, choices=radios[self._column])
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
            field += "\n" + h.content_tag("span", content=errors[self._column], class_=class_error)
        # Make the documentation
        if self._column in docs:
            field += "\n" + h.content_tag("span", content=docs[self._column], class_=class_doc)

        # Wrap the whole thing into a div
        field = utils.wrap("<div>", field, "</div>")

        return field
