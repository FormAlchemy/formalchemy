# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import logging
logger = logging.getLogger('formalchemy.' + __name__)

from copy import copy, deepcopy
import datetime

import helpers as h
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.attributes import ScalarAttributeImpl, ScalarObjectAttributeImpl, CollectionAttributeImpl
from sqlalchemy.orm.properties import CompositeProperty
from sqlalchemy.orm.exc import UnmappedClassError
import fatypes, validators

__all__ = ['Field', 'FieldRenderer', 'query_options']


class FieldRenderer(object):
    """
    This should be the super class of all xRenderer classes.

    This class takes a SQLAlchemy mapped class as first argument and the column
    name to process as second argument. It maps the column name as the field
    name and the column's value as the field's value.
    
    Subclasses should override `render`.
    
    Some subclasses, particularly subclasses that render as multiple
    form fields, may also wish to override `serialized_value`.
    (DateFieldRenderer is an example of this.)  !FormAlchemy knows
    how to deserialize standard data types, but for custom type support
    (e.g., for Composite values), you can override deserialize as well.
    Note that deserialize must be a staticmethod.

    You should not need to touch `name` or `value`.
    """
    def __init__(self, field):
        self.field = field
        assert isinstance(self.field, AbstractField)
        
    def name(self):
        """Field name"""
        clsname = self.field.model.__class__.__name__
        try:
            pk = _pk(self.field.model)
        except UnmappedClassError:
            pk = ''
        else:
            assert pk != ''
        if pk is None:
            pk = ''
        return '%s-%s-%s' % (clsname, pk, self.field.name)
    name = property(name)
        
    def value(self):
        """Current value, or default if none"""
        return self.field.value
    value = property(value)

    def render(self, **kwargs):
        """Render the field"""
        return h.text_field(self.name, value=self.value)

    def serialized_value(self):
        """
        Returns the appropriate value to deserialize for field's
        datatype, from the user-submitted data.
        
        This is broken out into a separate method so multi-input
        renderers can stitch their values back into a single one.
        
        Do not attempt to deserialize here; return value should be a
        string (corresponding to the output of `str` for your data
        type).
        """
        params = self.field.parent.data
        if not (hasattr(params, 'getall') and hasattr(params, 'getone')):
            raise Exception('unsupported params object.  currently only Paste-style multidicts are supported')
        if self.field.is_collection():
            return params.getall(self.name)
        return params.getone(self.name)

    def deserialize(data):
        raise NotImplementedError()
    deserialize = staticmethod(deserialize)
    

class TextFieldRenderer(FieldRenderer):
    def length(self):
        return self.field.type.length
    length = property(length)

    def render(self, **kwargs):
        return h.text_field(self.name, value=self.value, maxlength=self.length, **kwargs)


class IntegerFieldRenderer(FieldRenderer):
    def render(self, **kwargs):
        return h.text_field(self.name, value=self.value, **kwargs)


class PasswordFieldRenderer(TextFieldRenderer):
    def render(self, **kwargs):
        return h.password_field(self.name, value=self.value, maxlength=self.length, **kwargs)


class TextAreaFieldRenderer(FieldRenderer):
    def render(self, size, **kwargs):
        if isinstance(size, basestring):
            return h.text_area(self.name, content=self.value, size=size, **kwargs)
        else:
            cols, rows = size
            return h.text_area(self.name, content=self.value, cols=cols, rows=rows, **kwargs)


class HiddenFieldRenderer(FieldRenderer):
    def render(self, **kwargs):
        return h.hidden_field(self.name, value=self.value, **kwargs)


class BooleanFieldRenderer(FieldRenderer):
    def render(self, **kwargs):
        return h.check_box(self.name, True, checked=self.value, **kwargs)


class FileFieldRenderer(FieldRenderer):
    def render(self, **kwargs):
        # todo Do we need a value here ?
        return h.file_field(self.name, **kwargs)


class DateFieldRenderer(FieldRenderer):
    def _render(self, **kwargs):
        data = self.field.parent.data
        import calendar
        month_options = [('Month', 'MM')] + [(calendar.month_name[i], str(i)) for i in xrange(1, 13)]
        day_options = [('Day', 'DD')] + [(i, str(i)) for i in xrange(1, 32)]
        mm_name = self.name + '__month'
        dd_name = self.name + '__day'
        yyyy_name = self.name + '__year'
        # todo fix: "or ''"
        mm = (data is not None and mm_name in data) and data[mm_name] or str(self.value and self.value.month)
        dd = (data is not None and dd_name in data) and data[dd_name] or str(self.value and self.value.day)
        # could be blank so don't use and/or construct
        if data is not None and yyyy_name in data:
            yyyy = data[yyyy_name]
        else:
            yyyy = str(self.value and self.value.year or 'YYYY')
        return h.select(mm_name, h.options_for_select(month_options, selected=mm), **kwargs) \
               + ' ' + h.select(dd_name, h.options_for_select(day_options, selected=dd), **kwargs) \
               + ' ' + h.text_field(yyyy_name, value=yyyy, maxlength=4, size=4, **kwargs)
    def render(self, **kwargs):
        return h.content_tag('span', self._render(**kwargs), id=self.name)

    def serialized_value(self):
        return '-'.join([self.field.parent.data.getone(self.name + '__' + subfield) for subfield in ['year', 'month', 'day']])


class TimeFieldRenderer(FieldRenderer):
    def _render(self, **kwargs):
        data = self.field.parent.data
        hour_options = ['HH'] + [(i, str(i)) for i in xrange(24)]
        minute_options = ['MM' ] + [(i, str(i)) for i in xrange(60)]
        second_options = ['SS'] + [(i, str(i)) for i in xrange(60)]
        hh_name = self.name + '__hour'
        mm_name = self.name + '__minute'
        ss_name = self.name + '__second'
        hh = (data is not None and hh_name in data) and data[hh_name] or str(self.value and self.value.hour)
        mm = (data is not None and mm_name in data) and data[mm_name] or str(self.value and self.value.minute)
        ss = (data is not None and ss_name in data) and data[ss_name] or str(self.value and self.value.second)
        return h.select(hh_name, h.options_for_select(hour_options, selected=hh), **kwargs) \
               + ':' + h.select(mm_name, h.options_for_select(minute_options, selected=mm), **kwargs) \
               + ':' + h.select(ss_name, h.options_for_select(second_options, selected=ss), **kwargs)
    def render(self, **kwargs):
        return h.content_tag('span', self._render(**kwargs), id=self.name)

    def serialized_value(self):
        return ':'.join([self.field.parent.data.getone(self.name + '__' + subfield) for subfield in ['hour', 'minute', 'second']])


class DateTimeFieldRendererRenderer(DateFieldRenderer, TimeFieldRenderer):
    def render(self, **kwargs):
        return h.content_tag('span', DateFieldRenderer._render(self, **kwargs) + ' ' + TimeFieldRenderer._render(self, **kwargs), id=self.name)

    def serialized_value(self):
        return DateFieldRenderer.serialized_value(self) + ' ' + TimeFieldRenderer.serialized_value(self)


def _extract_options(options):
    if isinstance(options, dict):
        options = options.items()
    for choice in options:
        # Choice is a list/tuple...
        if isinstance(choice, (list, tuple)):
            if len(choice) != 2:
                raise Exception('Options should consist of two items, a name and a value; found %d items in %r' % (len(choice, choice)))
            yield choice
        # ... or just a string.
        else:
            if not isinstance(choice, basestring):
                raise Exception('List, tuple, or string value expected as option (got %r)' % choice)
            yield (choice, choice)


class RadioSet(FieldRenderer):
    widget = staticmethod(h.radio_button)

    def render(self, options, **kwargs):
        self.radios = []
        for choice_name, choice_value in _extract_options(options):
            radio = self.widget(self.name, choice_value, checked=self.value == choice_value, **kwargs)
            self.radios.append(radio + choice_name)
        return h.tag("br").join(self.radios)

class CheckBoxSet(RadioSet):
    widget = staticmethod(h.check_box)


class SelectFieldRenderer(FieldRenderer):
    def render(self, options, **kwargs):
        selected = kwargs.get('selected', None) or self.value
        return h.select(self.name, h.options_for_select(options, selected=selected), **kwargs)

    
def _pk(instance):
    # Return the value of this instance's primary key.
    column = class_mapper(type(instance)).primary_key[0]
    return getattr(instance, column.key)


def query_options(query):
    """
    Return a list of tuples of `(item description, item pk)`
    for each item returned by the query, where `item description`
    is the result of str(item) and `item pk` is the item's primary key.
    
    This list is suitable for using as a value for `options` parameters.
    """
    return [(str(item), _pk(item)) for item in query.all()]


def _foreign_keys(property):
    # 0.4/0.5 compatibility fn
    try:
        return property.foreign_keys
    except AttributeError:
        return [r for l, r in property.synchronize_pairs]


def _model_equal(a, b):
    if not isinstance(a, type):
        a = type(a)
    if not isinstance(b, type):
        b = type(b)            
    return a is b
    

class AbstractField(object):
    """
    Contains the information necessary to render (and modify the rendering of)
    a form field
    """
    def __init__(self, parent):
        # the FieldSet (or any ModelRenderer) owning this instance
        self.parent = parent
        if 0:
            import forms
            isinstance(self.parent, forms.FieldSet)
        # Renderer for this Field.  this will
        # be autoguessed, unless the user forces it with .dropdown,
        # .checkbox, etc.
        self._renderer = None
        # other render options, such as size, multiple, etc.
        self.render_opts = {}
        # validator functions added with .validate()
        self.validators = []
        # errors found by _validate() (which runs implicit and
        # explicit validators)
        self.errors = []
        # disabled or readonly
        self.modifier = None
        # label to use for the rendered field.  autoguessed if not specified by .label()
        self.label_text = None

    def __deepcopy__(self, memo):
        wrapper = copy(self)
        wrapper.render_opts = dict(self.render_opts)
        wrapper.validators = list(self.validators)
        wrapper.errors = list(self.errors)
        wrapper._renderer = copy(self._renderer)
        if hasattr(wrapper._renderer, 'field'):
            wrapper._renderer.field = wrapper
        return wrapper
                        
    def is_raw_foreign_key(self):
        """True iff this Field is a raw foreign key"""
        return False

    def is_pk(self):
        """True iff this Field is a primary key"""
        return False

    def query(self, *args, **kwargs):
        """Perform a query in the parent's session"""
        return self.parent.session.query(*args, **kwargs)
    
    def _validate(self):
        self.errors = []

        try:
            value = self._deserialize(self._serialized_value())
        except validators.ValidationError, e:
            self.errors.append(e)
            return False

        L = list(self.validators)
        if self.is_required() and validators.required not in L:
            L.append(validators.required)
        for validator in L:
            if validator is not validators.required and value is None:
                continue
            try:
                validator(value)
            except validators.ValidationError, e:
                self.errors.append(e.message)
        return not self.errors

    def is_required(self):
        """True iff this Field must be given a non-empty value"""
        return validators.required in self.validators
    
    def _deserialize(self, data):
        """convert data (serialized user data, or None) into the data type expected by field"""
        assert data is None or isinstance(data, basestring), '%r is not a string' % data
        try:
            return self.renderer.__class__.deserialize(data)
        except NotImplementedError:
            pass
        if isinstance(self.type, fatypes.Boolean):
            if data is None and isinstance(self.renderer, BooleanFieldRenderer):
                return False
            if data is not None:
                if data.lower() in ['1', 't', 'true', 'yes']: return True
                if data.lower() in ['0', 'f', 'false', 'no']: return False
        if data is None:
            return None
        if isinstance(self.type, fatypes.Integer):
            return validators.integer(data)
        if isinstance(self.type, fatypes.Float):
            return validators.float_(data)

        def _date(data):
            if data == 'YYYY-MM-DD' or data == '-MM-DD' or not data.strip():
                return None
            try:
                return datetime.date(*[int(st) for st in data.split('-')])
            except:
                raise validators.ValidationError('Invalid date')
        def _time(data):
            if data == 'HH:MM:SS' or not data.strip():
                return None
            try:
                return datetime.time(*[int(st) for st in data.split(':')])
            except:
                raise validators.ValidationError('Invalid time')
        
        if isinstance(self.type, fatypes.Date):
            return _date(data)
        if isinstance(self.type, fatypes.Time):
            return _time(data)
        if isinstance(self.type, fatypes.DateTime):
            data_date, data_time = data.split(' ')
            dt, tm = _date(data_date), _time(data_time)
            if dt is None and tm is None:
                return None
            elif dt is None or tm is None:
                raise validators.ValidationError('Incomplete datetime')
            return datetime.datetime(dt.year, dt.month, dt.day, tm.hour, tm.minute, tm.second)

        return data

    def model(self):
        return self.parent.model
    model = property(model)

    def _serialized_value(self):
        # data from user input suitable for _deserialize
        return self.renderer.serialized_value()
        
    def _modified(self, **kwattrs):
        # return a copy of self, with the given attributes modified
        copied = deepcopy(self)
        for attr, value in kwattrs.iteritems():
            setattr(copied, attr, value)
        return copied
    def bind(self, parent):
        """Return a copy of this Field, bound to a different parent"""
        return self._modified(parent=parent)
    def validate(self, validator):
        """ 
        Add the `validator` function to the list of validation
        routines to run when the `FieldSet`'s `validate` method is
        run. Validator functions take one parameter: the value to
        validate. This value will have already been turned into the
        appropriate data type for the given `Field` (string, int, float,
        etc.). It should raise `ValidationError` if validation
        fails with a message explaining the cause of failure.
        """
        field = deepcopy(self)
        field.validators.append(validator)
        return field
    def required(self):
        """
        Change the label associated with this field.  By default, the
        field name is used, modified for readability (e.g.,
        'user_name' -> 'User name').
        """
        return self.validate(validators.required)
    def label(self, text):
        """
        Change the label associated with this field.  By default, the field name
        is used, modified for readability (e.g., 'user_name' -> 'User name').
        """
        return self._modified(label_text=text)
    def disabled(self):
        """Render the field disabled."""
        return self._modified(modifier='disabled')
    def readonly(self):
        """Render the field readonly."""
        return self._modified(modifier='readonly')
    def hidden(self):
        """Render the field hidden.  (Value only, no label.)"""
        return self._modified(_renderer=HiddenFieldRenderer, render_opts={})
    def password(self):
        """Render the field as a password input, hiding its value."""
        field = deepcopy(self)
        field._renderer = lambda: self.parent.default_renderers['password']
        field.render_opts={}
        return field
    def textarea(self, size=None):
        """Render the field as a textarea."""
        field = deepcopy(self)
        field._renderer = lambda: self.parent.default_renderers['textarea']
        field.render_opts={'size': size}
    def radio(self, options=None):
        """Render the field as a set of radio buttons."""
        field = deepcopy(self)
        field._renderer = lambda: self.parent.default_renderers['radio']
        if options is None:
            options = self.render_opts.get('options')
        field.render_opts = {'options': options}
        return field
    def checkbox(self, options=None):
        """Render the field as a set of checkboxes."""
        field = deepcopy(self)
        field._renderer = lambda: field.parent.default_renderers['checkbox']
        if options is None:
            options = self.render_opts.get('options')
        field.render_opts = {'options': options}
        return field
    def dropdown(self, options=None, multiple=False, size=5):
        """
        Render the field as an HTML select field.  
        (With the `multiple` option this is not really a 'dropdown'.)
        """
        field = deepcopy(self)
        field._renderer = lambda: field.parent.default_renderers['dropdown']
        if options is None:
            options = self.render_opts.get('options')
        field.render_opts = {'multiple': multiple, 'options': options}
        if multiple:
            field.render_opts['size'] = size
        return field
    
    def _get_renderer(self):
        for t in self.parent.default_renderers:
            if not isinstance(t, basestring) and isinstance(self.type, t):
                return self.parent.default_renderers[t]
        return FieldRenderer
    
    def renderer(self):
        if self._renderer is None:
            self._renderer = self._get_renderer()
        if callable(self._renderer):
            # invoke potential lambda
            try:
                self._renderer = self._renderer()
            except TypeError:
                pass
        if callable(self._renderer):
            # must be a Renderer class.  instantiate.
            self._renderer = self._renderer(self)
        return self._renderer
    renderer = property(renderer)
    
    def render(self, **html_options):
        """
        Render this Field as HTML.
        
        `html_options` are not used by the default template, but are
        provided to make more customization possible in custom templates
        """
        opts = dict(self.render_opts)
        opts.update(html_options)
        if (isinstance(self.type, fatypes.Boolean) 
            and not opts.get('options') 
            and self.renderer.__class__ in [self.parent.default_renderers['dropdown'], self.parent.default_renderers['radio']]):
            opts['options'] = [('Yes', True), ('No', False)]
        return self.renderer.render(readonly=self.modifier=='readonly', disabled=self.modifier=='disabled', **opts)


class Field(AbstractField):
    """
    A manually-added form field
    """
    def __init__(self, name=None, type=fatypes.String, value=None):
        """
          * `name`: field name
          * `type`: data type, from sqlalchemy.types (Boolean, Integer, String)
          * `value`: default value.  If value is a callable, it will be passed
            the current bound model instance when the value is read.  This allows
            creating a Field whose value depends on the model once, then
            binding different instances to it later.
        """
        AbstractField.__init__(self, None) # parent will be set by ModelRenderer.add
        self.type = type()
        self.name = name
        self._value = value
        
    def value(self):
        if self.parent.data is not None and self.renderer.name in self.parent.data:
            try:
                v = self._deserialize(self._serialized_value())
            except validators.ValidationError:
                return self._serialized_value()
            if v is not None:
                return v
        if callable(self._value):
            return self._value(self.model)
        return self._value
    value = property(value)
        
    def key(self):
        return self.name
    key = property(key)

    def is_collection(self):
        return self.render_opts.get('multiple', False)
    
    def value_str(self):
        if self.is_collection():
            return [str(item) for item in self.value]
        return str(self.value)

    def sync(self):
        """Set the attribute's value in `model` to the value given in `data`"""
        self._value = self._deserialize(self._serialized_value())
            
    def __repr__(self):
        return 'AttributeField(%s)' % self.name
    
    def __eq__(self, other):
        # we override eq so that when we configure with options=[...], we can match the renders in options
        # with the ones that were generated at FieldSet creation time
        try:
            return self.name == other.name and _model_equal(self.model, other.model)
        except (AttributeError, ValueError):
            return False
    def __hash__(self):
        return hash(self.name)

    def _deserialize(self, st):
        if self.is_collection():
            return [AbstractField._deserialize(self, id_st)
                    for id_st in st]
        return AbstractField._deserialize(self, st)


class AttributeField(AbstractField):
    """
    Field corresponding to an SQLAlchemy attribute.
    """
    def __init__(self, instrumented_attribute, parent):
        AbstractField.__init__(self, parent)
        # we rip out just the parts we care about from InstrumentedAttribute.
        # impl is the AttributeImpl.  So far all we care about there is ".key,"
        # which is the name of the attribute in the mapped class.
        self._impl = instrumented_attribute.impl
        # property is the PropertyLoader which handles all the interesting stuff.
        # mapper, columns, and foreign keys are all located there.
        self._property = instrumented_attribute.property
        # smarter default "required" value
        if not self.is_collection() and not self._column.nullable:
            self.validators.append(validators.required)
            
    def is_raw_foreign_key(self):
        try:
            return _foreign_keys(self._property.columns[0])
        except AttributeError:
            return False
        
    def is_pk(self):
        return self._column.primary_key
    
    def type(self):
        if self.is_composite():
            # this is a little confusing -- we need to return an _instance_ of
            # the correct type, which for composite values will be the value
            # itself. SA should probably have called .type something
            # different, or just not instantiated them...
            return self.parent.model
        return self._column.type
    type = property(type)

    def _column(self):
        # todo this does not allow handling composite attributes (PKs or FKs)
        if isinstance(self._impl, ScalarObjectAttributeImpl):
            # If the attribute is a foreign key, return the Column that this
            # attribute is mapped from -- e.g., .user -> .user_id. 
            return _foreign_keys(self._property)[0]
        elif isinstance(self._impl, ScalarAttributeImpl):
            # normal property, mapped to a single column from the main table
            return self._property.columns[0]
        else:
            # collection -- use the mapped class's PK
            assert isinstance(self._impl, CollectionAttributeImpl)
            return self._property.mapper.primary_key[0]
    _column = property(_column)
    
    def key(self):
        """The name of the attribute in the class"""
        return self._impl.key
    key = property(key)

    def name(self):
        """ 
        The name of the form input. usually the same as the column name, except for
        multi-valued SA relation properties. For example, for order.user,
        name will be 'user_id' (assuming that is indeed the name of the foreign
        key to users), but for user.orders, name will be 'orders'.
        """
        if self.is_collection() or self.is_composite():
            return self.key
        return self._column.name
    name = property(name)
    
    def is_collection(self):
        """True iff this is a multi-valued (one-to-many or many-to-many) SA relation"""
        return isinstance(self._impl, CollectionAttributeImpl)
    
    def is_composite(self):
        return isinstance(self._property, CompositeProperty)
    
    def is_vanilla(self):
        """True iff this is a simple scalar value mapped from a table"""
        return not (isinstance(self._impl, ScalarObjectAttributeImpl) or self.is_collection())
    
    def collection_type(self):
        """The type of object in the collection (e.g., `User`).  Calling this is only valid when `is_collection()` is True"""
        return self._property.mapper.class_
    
    def value(self):
        """
        The value of this Field: use the corresponding value in the bound `data`,
        if any; otherwise, use the value in the bound `model`.  If there is still no
        value, use the default defined on the corresponding `Column`.
        
        For collections,
        a list of the primary key values of the items in the collection is returned.
        """
        if self.parent.data is not None and self.renderer.name in self.parent.data:
            try:
                v = self._deserialize(self._serialized_value())
            except validators.ValidationError:
                v = self._serialized_value()
        else:
            v = getattr(self.model, self.name)
        if self.is_collection():
            return [_pk(item) for item in v]
        if v is not None:
            return v
        if self._column.default:
            if callable(self._column.default.arg):
                # callables often depend on the current time, e.g. datetime.now or the equivalent SQL function.
                # these are meant to be the value *at insertion time*, so it's not strictly correct to
                # generate a value at form-edit time.
                pass
            else:
                return self._column.default
        return None
    value = property(value)
    
    def value_str(self):
        """A string representation of `value` for use in non-editable contexts (so we don't check 'data')"""
        if self.is_collection():
            L = getattr(self.model, self.key)
            return ','.join([str(item) for item in L])
        else:
            return str(getattr(self.model, self.key))
        
    def sync(self):
        """Set the attribute's value in `model` to the value given in `data`"""
        setattr(self.model, self.name, self._deserialize(self._serialized_value()))
            
    def __eq__(self, other):
        # we override eq so that when we configure with options=[...], we can match the renders in options
        # with the ones that were generated at FieldSet creation time
        try:
            return self._impl is other._impl and _model_equal(self.model, other.model)
        except (AttributeError, ValueError):
            return False
    def __hash__(self):
        return hash(self._impl)
    
    def __repr__(self):
        return 'AttributeField(%s)' % self.key
    
    # todo add .options method (for html_options)
    
    def render(self, **html_options):
        if not self.is_vanilla() and not self.render_opts.get('options'):
            # todo this does not handle primaryjoin (/secondaryjoin) alternate join conditions
            fk_cls = self.collection_type()
            fk_pk = class_mapper(fk_cls).primary_key[0]
            q = self.parent.session.query(fk_cls).order_by(fk_pk)
            self.render_opts['options'] = query_options(q)
            logger.debug('options for %s are %s' % (self.name, self.render_opts['options']))
        if self.is_collection() and isinstance(self.renderer, self.parent.default_renderers['dropdown']):
            self.render_opts['multiple'] = True
            if 'size' not in self.render_opts:
                self.render_opts['size'] = 5
        return AbstractField.render(self, **html_options)

    def _get_renderer(self):
        if isinstance(self._impl, ScalarObjectAttributeImpl) or self.is_collection():
            return self.parent.default_renderers['dropdown']
        return AbstractField._get_renderer(self)

    def _deserialize(self, st):
        if self.is_collection():
            return [self.query(self.collection_type()).get(AbstractField._deserialize(self, id_st))
                    for id_st in st]
        return AbstractField._deserialize(self, st)
