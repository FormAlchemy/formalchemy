# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import logging
logger = logging.getLogger('formalchemy.' + __name__)

import helpers as h
import sqlalchemy.types as types
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.attributes import ScalarAttributeImpl, ScalarObjectAttributeImpl, CollectionAttributeImpl
import base

__all__ = ["TextField", "PasswordField", "HiddenField", "BooleanField",
    "FileField", "IntegerField", "DateTimeField", "DateField", "TimeField",
    "RadioSet", "SelectField"]

class ModelFieldRender(object):
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

    def __init__(self, attr, **kwargs):
        self.attr = attr
        self.attribs = kwargs
        
    def name(self):
        return self.attr.name
    name = property(name)
        
    def value(self):
        return self.attr.value
    value = property(value)

    def render(self):
        return h.text_field(self.name, value=self.value)

class TextField(ModelFieldRender):
    """The `TextField` class."""

    def __init__(self, attr, **kwargs):
        super(TextField, self).__init__(attr, **kwargs)
        self.length = attr.column.type.length

    def render(self):
        return h.text_field(self.name, value=self.value, maxlength=self.length, **self.attribs)

class PasswordField(TextField):
    """The `PasswordField` class."""

    def render(self):
        return h.password_field(self.name, value=self.value, maxlength=self.length, **self.attribs)

class TextAreaField(ModelFieldRender):
    """The `TextAreaField` class."""

    def __init__(self, attr, size, **kwargs):
        super(TextAreaField, self).__init__(attr, **kwargs)
        self.size = size

    def render(self):
        if isinstance(self.size, basestring):
            return h.text_area(self.name, content=self.value, size=self.size, **self.attribs)
        else:
            # Will fail if not a 2-item list or tuple. 
            cols, rows = self.size
            return h.text_area(self.name, content=self.value, cols=cols, rows=rows, **self.attribs)

class HiddenField(ModelFieldRender):
    """The `HiddenField` class."""

    def render(self):
        return h.hidden_field(self.name, value=self.value, **self.attribs)

class BooleanField(ModelFieldRender):
    """The `BooleanField` class."""

    def render(self):
        # This is a browser hack to have a checkbox POSTed as False even if it wasn't
        # checked, as unchecked boxes are not POSTed. The hidden field should be *after* the checkbox.
        return h.check_box(self.name, True, checked=self.value, **self.attribs) + h.hidden_field(self.name, value=False)

class FileField(ModelFieldRender):
    """The `FileField` class."""

    def render(self):
        # Do we need a value here ?
        return h.file_field(self.name, **self.attribs)

class IntegerField(ModelFieldRender):
    """The `IntegerField` class."""

    def render(self):
        return h.text_field(self.name, value=self.value, **self.attribs)

class ModelDateTimeRender(ModelFieldRender):
    """The `ModelDateTimeRender` class.

    This should be the super class for (Date|Time|DateTime)Field.

    """

    def __init__(self, attr, format, **kwargs):
        super(ModelDateTimeRender, self).__init__(attr, **kwargs)
        self.format = format

    def get_value(self):
        value = super(ModelDateTimeRender, self).get_value()
        if value is not None:
            return value.strftime(self.format)
        else:
            if not callable(self.default):
                return self.default

    def render(self):
        return h.text_field(self.name, value=self.value, **self.attribs)

class DateTimeField(ModelDateTimeRender):
    """The `DateTimeField` class."""
    pass

class DateField(ModelDateTimeRender):
    """The `DateField` class."""
    pass

class TimeField(ModelDateTimeRender):
    """The `TimeField` class."""
    pass

class RadioField:
    """The `RadioField` class."""

    def __init__(self, name, value, **kwargs):
        self.name = name
        self.value = value
        self.attribs = kwargs

    def render(self):
        return h.radio_button(self.name, self.value, **self.attribs)

class RadioSet(ModelFieldRender):
    """The `RadioSet` class."""

    def __init__(self, attr, choices, **kwargs):
        super(RadioSet, self).__init__(attr)

        radios = []

        if isinstance(choices, dict):
            choices = choices.items()

        for choice in choices:
            # Choice is a list/tuple...
            if isinstance(choice, (list, tuple)):
                choice_name, choice_value = choice
                radio = RadioField(self.name, choice_value, checked=self.value == choice_value, **kwargs)
                radios.append(radio.render() + choice_name)
            # ... a boolean...
            elif isinstance(choice, bool):
                radio = RadioField(self.name, choice, checked=self.value == choice, **kwargs)
                radios.append(radio.render() + str(choice))
#                radios.append("\n" + h.radio_button(self.name, choice, checked=self.value == choice) + str(choice))
            # ... or just a string.
            else:
                checked = choice == attr.value or choice == self.default
                radios.append("\n" + h.radio_button(attr.name, choice, checked=checked, **kwargs) + choice)

        self.radios = radios

    def render(self):
        return h.tag("br").join(self.radios)

class SelectField(ModelFieldRender):
    """The `SelectField` class."""

    def __init__(self, attr, options, **kwargs):
        self.options = options
        selected = kwargs.get('selected', None)
        super(SelectField, self).__init__(attr, **kwargs)
        self.selected = selected or self.value

    def render(self):
        return h.select(self.name, h.options_for_select(self.options, selected=self.selected), **self.attribs)
    
def _pk(instance):
    column = class_mapper(type(instance)).primary_key[0]
    return getattr(instance, column.key)

class AttributeWrapper:
    def __init__(self, data):
        if isinstance(data, AttributeWrapper):
            self.__dict__.update(data.__dict__)
            self.render_opts = dict(data.render_opts)
        else:
            instrumented_attribute, self.model, self.session = data
            self._impl = instrumented_attribute.impl
            self._property = instrumented_attribute.property
            self.render_as = None
            self.render_opts = {}
            self.modifier = None
            self.label_text = None
                        
    def is_raw_foreign_key(self):
        try:
            return self._property.columns[0].foreign_keys
        except AttributeError:
            return False

    def column(self):
        if isinstance(self._impl, ScalarObjectAttributeImpl):
            return self._property.foreign_keys[0]
        elif isinstance(self._impl, ScalarAttributeImpl):
            return self._property.columns[0]
        else:
            assert isinstance(self._impl, CollectionAttributeImpl)
            return self._property.mapper.primary_key[0]
    column = property(column)

    def key(self):
        """The name of the attribute in the class"""
        return self._impl.key
    key = property(key)

    def name(self):
        """ 
        The name of the form input. usually the same as 'key', except for
        single-valued SA relation properties. For example, for order.user,
        name will be user_id (assuming that is indeed the name of the foreign
        key to users) 
        """
        if self.is_collection():
            return self._impl.key
        return self.column.name
    name = property(name)

    def is_collection(self):
        return isinstance(self._impl, CollectionAttributeImpl)
    
    def value(self):
        v = getattr(self.model, self.name)
        if self.is_collection():
            return [_pk(item) for item in v]
        if v is not None:
            return v
        if self.column.default:
            if callable(self.column.default.arg):
                logger.info('Ignoring callable default value for %s' % self)
            else:
                return self.column.default
        return None
    value = property(value)
    
    def value_str(self):
        if self.is_collection():
            L = getattr(self.model, self._impl.key)
            return ','.join([str(item) for item in L])
        else:
            return str(getattr(self.model, self._impl.key))

    def nullable(self):
        return self.column.nullable
    nullable = property(nullable)
    
    def __eq__(self, other):
        try:
            return self._impl is other._impl
        except (AttributeError, ValueError):
            return False
    def __hash__(self):
        return hash(self._impl)
    
    def __repr__(self):
        return 'AttributeWrapper(%s)' % self._impl.key

    def label(self, text):
        attr = AttributeWrapper(self)
        attr.label_text = text
        return attr
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
        return self.render_as(self, readonly=self.modifier=='readonly', disabled=self.modifier=='disabled', **self.render_opts).render()
    def _get_render_as(self):
        if isinstance(self._impl, ScalarObjectAttributeImpl) or self.is_collection():
            if 'options' not in self.render_opts:
                logger.debug('loading options for ' + self.name)
                fk_cls = self._property.mapper.class_
                fk_pk = class_mapper(fk_cls).primary_key[0]
                items = self.session.query(fk_cls).order_by(fk_pk).all()
                self.render_opts['options'] = [(str(item), _pk(item)) for item in items]
            self.render_opts['multiple'] = self.is_collection() # todo make default size bigger than 1
            if self.render_opts['multiple'] and 'size' not in self.render_opts:
                self.render_opts['size'] = 5
            return SelectField
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
