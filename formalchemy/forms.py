# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import logging
logger = logging.getLogger('formalchemy.' + __name__)

import webhelpers as h
import base, fields, utils

__all__ = ["FieldSet", "Field"]

class FieldSet(base.BaseModelRender):
    """The `FieldSet` class.

    This class is responsible for generating HTML fields from a given
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
      everytime you call `render` or FormAlchemy will fallback to its
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
    
    def get_pks(self):
        """Return a list of primary key attributes."""
        return [wrapper for wrapper in self.get_attrs() if wrapper.column.primary_key]

    def get_required(self):
        """Return a list of non-nullable attributes."""
        return [wrapper for wrapper in self.get_attrs() if not wrapper.column.nullable]

    def render(self, **options):
        # Merge class level options with given options.
        opts = self.new_options(**options)
        logger.debug(opts)

        # Filter out unnecessary columns.
        attrs = self.get_attrs(**opts)

        html = []
        # Generate fields.
        field_render = Field(self.model, self.session)
        field_render.reconfigure(**opts)
        for attr in attrs:
            field_render.set_attr(attr)
            field = field_render.render()
            html.append(field)

        return "\n".join(html)


class Field(base.BaseColumnRender):
    """The `Field` class.

    Return generated HTML <label> and <input> tags for one single column.

    """

    def __init__(self, model, session=None, attr=None, make_label=True):
        super(Field, self).__init__(model, session, attr=attr)

        self.set_make_label(make_label)
        self._focus_rendered = False

    def set_make_label(self, value):
        self._make_label = bool(value)

    def get_make_label(self):
        return self._make_label

    def render(self, **options):
        # Merge class level options with given options.
        opts = self.new_options(**options)

        # DateTime, Date, Time string formaters
        date_f = opts.get('date', "%Y-%m-%d")
        time_f = opts.get('time', "%H:%M:%S")
        datetime_f = opts.get('datetime', "%s %s" % (date_f, time_f))

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
        if self.wrapper.render_as == fields.HiddenField:
            return self.wrapper.render()

        # Make the label
        field = ""

        if make_label:
            label = fields.Label(self.wrapper.column, alias=alias.get(self.wrapper.name, self.wrapper.name))
            label.set_prettify(pretty_func)
            if self.wrapper.nullable:
                label.cls = cls_fld_opt
            else:
                label.cls = cls_fld_req
            field += label.render()

        # Make the input
        
        field += '\n' + self.wrapper.render()

        # Make the error
        if self.wrapper.column in errors:
            field += "\n" + h.content_tag("span", errors[self.wrapper.column], class_=cls_span_err)
        # Make the documentation
        if self.wrapper.column in docs:
            field += "\n" + h.content_tag("span", docs[self.wrapper.column], class_=cls_span_doc)

        if field.startswith("\n"):
            field = field[1:]

        # Wrap the whole thing into a div
        if self.get_make_label():
            field = utils.wrap("<div>", field, "</div>")

        # Do the field focusing
        if (focus == self.wrapper.column or focus is True) and not self._focus_rendered:
            field += "\n" + h.javascript_tag('document.getElementById("%s").focus();' % self.wrapper.name)
            self._focus_rendered = True

        return field
