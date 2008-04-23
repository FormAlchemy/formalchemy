# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import webhelpers as h
import sqlalchemy.types as types
import base

__all__ = ["Label", "TextField", "PasswordField", "HiddenField", "BooleanField",
    "FileField", "IntegerField", "DateTimeField", "DateField", "TimeField",
    "RadioSet", "SelectField"]

class Label(base.BaseRender):
    """The `Label` class."""

    def __init__(self, col, **kwargs):
        self.name = col.name
        self.alias = kwargs.get('alias', self.name)
        self.cls = kwargs.get('cls', None)
        self.set_prettify(kwargs.get('prettify', self.prettify))

    def get_display(self):
        return self.prettify(self.alias)

    def render(self):
        return h.content_tag("label", content=self.get_display(), for_=self.name, class_=self.cls)

class BaseFieldRender(base.BaseRender):
    """The `BaseFieldRender` class.

    This is the class that fits to all HTML <input> structure. It takes a
    field name and field value as argument.

    """

    def __init__(self, name, value):
        assert isinstance(name, basestring)
        self.name = name
        self.value = value

class ModelFieldRender(BaseFieldRender):
    """The `ModelFieldRender` class.

    This should be the super class of all xField classes.

    This class takes a SQLAlchemy mapped class as first argument and the column
    name to process as second argument. It maps the column name as the field
    name and the column's value as the field's value.

    Methods:
      * `get_value(self)`
        Return the column's current value if not None, otherwise
        return the default column value if available.
      * `render(self)`
        Return generated HTML.

    """

    def __init__(self, model, colname, **kwargs):
        super(ModelFieldRender, self).__init__(colname, getattr(model, colname))
        self.model = model
        if model.c[colname].default:
            self.default = model.c[colname].default.arg
        else:
            self.default = model.c[colname].default
        self.attribs = kwargs

    def get_value(self):
        if self.value is not None:
            return self.value
        else:
            if not callable(self.default):
                return self.default

    def render(self):
        return h.text_field(self.name, value=self.get_value())

class TextField(ModelFieldRender):
    """The `TextField` class."""

    def __init__(self, model, colname, **kwargs):
        super(TextField, self).__init__(model, colname, **kwargs)
        self.length = model.c[colname].type.length

    def render(self):
        return h.text_field(self.name, value=self.get_value(), maxlength=self.length, **self.attribs)

class PasswordField(TextField):
    """The `PasswordField` class."""

    def render(self):
        return h.password_field(self.name, value=self.get_value(), maxlength=self.length, **self.attribs)

class TextAreaField(ModelFieldRender):
    """The `TextAreaField` class."""

    def __init__(self, model, colname, size, **kwargs):
        super(TextAreaField, self).__init__(model, colname, **kwargs)
        self.size = size

    def render(self):
        if isinstance(self.size, basestring):
            return h.text_area(self.name, content=self.get_value(), size=self.size, **self.attribs)
        else:
            # Will fail if not a 2-item list or tuple. 
            cols, rows = self.size
            return h.text_area(self.name, content=self.get_value(), cols=cols, rows=rows, **self.attribs)

class HiddenField(ModelFieldRender):
    """The `HiddenField` class."""

    def render(self):
        return h.hidden_field(self.name, value=self.get_value(), **self.attribs)

class BooleanField(ModelFieldRender):
    """The `BooleanField` class."""

    def render(self):
        # This is a browser hack to have a checkbox POSTed as False even if it wasn't
        # checked, as unchecked boxes are not POSTed. The hidden field should be *after* the checkbox.
        return h.check_box(self.name, True, checked=self.get_value(), **self.attribs) + h.hidden_field(self.name, value=False)

class FileField(ModelFieldRender):
    """The `FileField` class."""

    def render(self):
        # Do we need a value here ?
        return h.file_field(self.name, **self.attribs)

class IntegerField(ModelFieldRender):
    """The `IntegerField` class."""

    def render(self):
        return h.text_field(self.name, value=self.get_value(), **self.attribs)

class ModelDateTimeRender(ModelFieldRender):
    """The `ModelDateTimeRender` class.

    This should be the super class for (Date|Time|DateTime)Field.

    """

    def __init__(self, model, colname, format, **kwargs):
        super(ModelDateTimeRender, self).__init__(model, colname, **kwargs)
        self.format = format

    def get_value(self):
        if self.value is not None:
            return self.value.strftime(self.format)
        else:
            if not callable(self.default):
                return self.default

    def render(self):
        return h.text_field(self.name, value=self.get_value(), **self.attribs)

class DateTimeField(ModelDateTimeRender):
    """The `DateTimeField` class."""
    pass

class DateField(ModelDateTimeRender):
    """The `DateField` class."""
    pass

class TimeField(ModelDateTimeRender):
    """The `TimeField` class."""
    pass

class RadioField(BaseFieldRender):
    """The `RadioField` class."""

    def __init__(self, name, value, **kwargs):
        super(RadioField, self).__init__(name, value)
        self.attribs = kwargs

    def render(self):
        return h.radio_button(self.name, self.value, **self.attribs)

class RadioSet(ModelFieldRender):
    """The `RadioSet` class."""

    def __init__(self, model, colname, choices, **kwargs):
        super(RadioSet, self).__init__(model, colname)

        radios = []

        if isinstance(choices, dict):
            choices = choices.items()

        for choice in choices:
            # Choice is a list/tuple...
            if isinstance(choice, (list, tuple)):
                choice_name, choice_value = choice
                radio = RadioField(self.name, choice_value, checked=self.get_value() == choice_value, **kwargs)
                radios.append(radio.render() + choice_name)
            # ... a boolean...
            elif isinstance(choice, bool):
                radio = RadioField(self.name, choice, checked=self.get_value() == choice, **kwargs)
                radios.append(radio.render() + str(choice))
#                radios.append("\n" + h.radio_button(self.name, choice, checked=self.get_value() == choice) + str(choice))
            # ... or just a string.
            else:
                checked = choice == getattr(self.model, colname) or choice == self.default
                radios.append("\n" + h.radio_button(colname, choice, checked=checked, **kwargs) + choice)

        self.radios = radios

    def render(self):
        return h.tag("br").join(self.radios)

class SelectField(ModelFieldRender):
    """The `SelectField` class."""

    def __init__(self, model, colname, options, **kwargs):
        self.options = options
        selected = kwargs.get('selected', None)
        super(SelectField, self).__init__(model, colname, **kwargs)
        self.selected = selected or self.get_value()

    def render(self):
        return h.select(self.name, h.options_for_select(self.options, selected=self.selected), **self.attribs)

class AttributeWrapper:
    def __init__(self, data):
        if isinstance(data, AttributeWrapper):
            self.__dict__.update(data.__dict__)
        else:
            instrumented_attribute, model = data
            self.model = model
            self.impl = instrumented_attribute.impl
            self._property = instrumented_attribute.property
            self.render_as = None
            self.render_opts = {}
            self.modifier = None

    def column(self):
        return self._property.columns[0]
    column = property(column)

    def name(self):
        return self.column.name
    name = property(name)

    def nullable(self):
        return self.column.nullable
    nullable = property(nullable)
    
    def __eq__(self, other):
        try:
            return self.column is other.column
        except ValueError:
            return False
    def __hash__(self):
        return hash(self.column)
    
    def __repr__(self):
        return 'AttributeWrapper(%s)' % self.name

    def disabled(self):
        attr = AttributeWrapper(self)
        attr.modifier = 'disabled'
        return attr
    def readonly(self):
        attr = AttributeWrapper(self)
        attr.modifier = 'readonly'
        return attr
    def hidden(self):
        attr = AttributeWrapper(self)
        attr.render_as = HiddenField
        attr.render_opts = {}
        return attr
    def password(self):
        attr = AttributeWrapper(self)
        attr.render_as = PasswordField
        attr.render_opts = {}
        return attr
    def textarea(self, size=None):
        attr = AttributeWrapper(self)
        attr.render_as = TextAreaField
        attr.render_opts = {'size': size}
        return attr
    def radio(self, choices=[]):
        if isinstance(self.column.type, types.Boolean) and not choices:
            choices = [True, False]
        attr = AttributeWrapper(self)
        attr.render_as = RadioSet
        attr.render_opts = {'choices': choices}
        return attr
    def dropdown(self, options=[], multiple=False):
        attr = AttributeWrapper(self)
        attr.render_as = SelectField
        attr.render_opts = {'multiple': multiple, 'options': options}
        return attr
    def render(self):
        if not self.render_as:
            self.render_as = self._get_render_as()
        return self.render_as(self.model, self.name, readonly=self.modifier=='readonly', disabled=self.modifier=='disabled', **self.render_opts).render()
    def _get_render_as(self):
        if isinstance(self.column.type, types.String):
            return TextField
        elif isinstance(self.column.type, types.Integer):
            return IntegerField
        elif isinstance(self.column.type, types.Boolean):
            return BooleanField
        elif isinstance(self.column.type, types.DateTime):
            return DateTimeField
        elif isinstance(self.column.type, types.Date):
            return DateField
        elif isinstance(self.column.type, types.Time):
            return TimeField
        elif isinstance(self.column.type, types.Binary):
            return FileField
        return ModelFieldRender
