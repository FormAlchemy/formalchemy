# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import webhelpers as h
import base

__all__ = ["Label", "TextField", "PasswordField", "HiddenField", "BooleanField",
    "FileField", "IntegerField", "DateTimeField", "DateField", "TimeField",
    "RadioSet", "SelectField"]

class Label(base.BaseRender):
    """The `Label` class."""

    def __init__(self, col, **kwargs):
        self.name = col
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

    def __init__(self, model, col, **kwargs):
        super(ModelFieldRender, self).__init__(col, getattr(model, col))
        self.model = model
        if model.c[col].default:
            self.default = model.c[col].default.arg
        else:
            self.default = model.c[col].default
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

    def __init__(self, model, col, **kwargs):
        super(TextField, self).__init__(model, col, **kwargs)
        self.length = model.c[col].type.length

    def render(self):
        return h.text_field(self.name, value=self.get_value(), maxlength=self.length, **self.attribs)

class PasswordField(TextField):
    """The `PasswordField` class."""

    def render(self):
        return h.password_field(self.name, value=self.get_value(), maxlength=self.length, **self.attribs)

class TextAreaField(ModelFieldRender):
    """The `TextAreaField` class."""

    def __init__(self, model, col, size, **kwargs):
        super(TextAreaField, self).__init__(model, col, **kwargs)
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

    def __init__(self, model, col, format, **kwargs):
        super(ModelDateTimeRender, self).__init__(model, col, **kwargs)
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

    def __init__(self, model, col, choices, **kwargs):
        super(RadioSet, self).__init__(model, col)

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
                checked = choice == getattr(self.model, col) or choice == self.default
                radios.append("\n" + h.radio_button(col, choice, checked=checked, **kwargs) + choice)

        self.radios = radios

    def render(self):
        return h.tag("br").join(self.radios)

class SelectField(ModelFieldRender):
    """The `SelectField` class."""

    def __init__(self, model, col, options, **kwargs):
        self.options = options
        selected = kwargs.get('selected', None)
        super(SelectField, self).__init__(model, col, **kwargs)
        self.selected = selected or self.get_value()

    def render(self):
        return h.select(self.name, h.options_for_select(self.options, selected=self.selected), **self.attribs)
