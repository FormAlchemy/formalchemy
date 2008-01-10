# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import webhelpers as h
import sqlalchemy.types as types

import formalchemy.base as base
import formalchemy.fields as fields
import formalchemy.utils as utils

#__all__ = ["FieldSet", "MultiFields", "Field"]
__all__ = ["FieldSet", "Field"]

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

        # Merge class level options with given options.
        opts = self.new_options(**options)

        legend = opts.get('legend', None)
        fieldset = opts.get('fieldset', True)

        model_render = MultiFields(self.model)
        # Reset options and only render based given options
        model_render.reconfigure(**opts)
        html = model_render.render()

        if not fieldset:
            return html

        # Setup class's name as default.
        if legend is None:
            legend_txt = self.model.__class__.__name__
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

        # Merge class level options with given options.
        opts = self.new_options(**options)

        # Filter out unnecessary columns.
        columns = self.get_colnames(**opts)

        # Should we keep track of rendered columns ?
        track_cols = opts.get('track_cols', False)

        # Add hidden fields.
        hiddens = opts.get('hidden', [])
        if isinstance(hiddens, basestring):
            hiddens = [hiddens]

        columns += hiddens

        # Store rendered columns in a hidden field.
#        if track_cols:
#            .append(col)

        html = []
        # Generate fields.
        field_render = Field(bind=self.model)
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

    def __init__(self, bind=None, column=None, make_label=True):
        super(Field, self).__init__(bind=bind, column=column)

        self.set_make_label(make_label)
        self._focus_rendered = False

    def set_make_label(self, value):
        self._make_label = bool(value)

    def get_make_label(self):
        return self._make_label

    def render(self, **options):
        super(Field, self).render()

        # Merge class level options with given options.
        opts = self.new_options(**options)

        # Categorize options
        readonlys = self.get_readonlys(**opts)

        passwords = opts.get('password', [])
        textareas = opts.get('textarea', {})
        if isinstance(passwords, basestring):
            passwords = [passwords]
        hiddens = opts.get('hidden', [])
        if isinstance(hiddens, basestring):
            hiddens = [hiddens]
        dropdowns = opts.get('dropdown', {})
        radios = opts.get('radio', {})
        bool_as_radio = opts.get('bool_as_radio', {})
        if isinstance(bool_as_radio, basestring):
            bool_as_radio = [bool_as_radio]

        make_label = opts.get('make_label', self.get_make_label())

        pretty_func = opts.get('prettify')
        alias = opts.get('alias', {})
        focus = opts.get('focus', True)

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
            return fields.HiddenField(self.model, self._column).render()

        # Make the label
        field = ""

        if make_label:
            label = fields.Label(self._column, alias=alias.get(self._column, self._column))
            label.set_prettify(pretty_func)
            if self.is_nullable(self._column):
                label.cls = cls_fld_opt
            else:
                label.cls = cls_fld_req
            field += label.render()

        # Hold a list of column names by type.
        col_types = self.get_coltypes()

        # Make the input
        if self._column in radios:
            radio = fields.RadioSet(self.model, self._column, choices=radios[self._column])
            field += "\n" + radio.render()

        elif self._column in dropdowns:
            # FIXME: Keeping 'opts' in dropdowns will send opts as attributes to the <select> tag.
            # But should we loose that info during rendering ?
            dropdown = fields.SelectField(self.model, self._column, dropdowns[self._column].pop("opts"), **dropdowns[self._column])
            field += "\n" + dropdown.render()

        elif self._column in passwords:
            field += "\n" + fields.PasswordField(self.model, self._column, readonly=self._column in readonlys).render()

        elif self._column in col_types[types.String]:
            if self._column in textareas:
                field += "\n" + fields.TextAreaField(self.model, self._column, size=textareas[self._column]).render()
            else:
                field += "\n" + fields.TextField(self.model, self._column).render()

        elif self._column in col_types[types.Integer]:
            field += "\n" + fields.IntegerField(self.model, self._column).render()

        elif self._column in col_types[types.Boolean]:
            if self._column in bool_as_radio:
                radio = fields.RadioSet(self.model, self._column, choices=[True, False])
                field += "\n" + radio.render()
            else:
                field += "\n" + fields.BooleanField(self.model, self._column).render()
#            # This is for radio style True/False rendering.
#            radio = fields.RadioSet(self.model, self._column, choices=[True, False])
#            field += "\n" + radio.render()

        elif self._column in col_types[types.DateTime]:
            field += "\n" + fields.DateTimeField(self.model, self._column).render()

        elif self._column in col_types[types.Date]:
            field += "\n" + fields.DateField(self.model, self._column).render()

        elif self._column in col_types[types.Time]:
            field += "\n" + fields.TimeField(self.model, self._column).render()

        elif self._column in col_types[types.Binary]:
            field += "\n" + fields.FileField(self.model, self._column).render()

        else:
            field += "\n" + fields.ModelFieldRender(self.model, self._column).render()

        # Make the error
        if self._column in errors:
            field += "\n" + h.content_tag("span", errors[self._column], class_=cls_span_err)
        # Make the documentation
        if self._column in docs:
            field += "\n" + h.content_tag("span", docs[self._column], class_=cls_span_doc)

        if field.startswith("\n"):
            field = field[1:]

        # Wrap the whole thing into a div
        if self.get_make_label():
            field = utils.wrap("<div>", field, "</div>")

        # Do the field focusing
        if (focus == self._column or focus is True) and not self._focus_rendered:
            field += "\n" + h.javascript_tag('document.getElementById("%s").focus();' % self._column)
            self._focus_rendered = True

        return field
