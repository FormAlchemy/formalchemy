# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import os
import cgi
import logging
logger = logging.getLogger('formalchemy.' + __name__)

from copy import copy, deepcopy
import datetime

import helpers as h
from sqlalchemy.orm import class_mapper, Query
from sqlalchemy.orm.attributes import ScalarAttributeImpl, ScalarObjectAttributeImpl, CollectionAttributeImpl, InstrumentedAttribute
from sqlalchemy.orm.properties import CompositeProperty
# from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy.exceptions import InvalidRequestError # 0.4 support
import fatypes, validators
from i18n import _

__all__ = ['Field', 'FieldRenderer',
           'TextFieldRenderer', 'TextAreaFieldRenderer',
           'PasswordFieldRenderer', 'HiddenFieldRenderer',
           'DateFieldRenderer', 'TimeFieldRenderer',
           'DateTimeFieldRenderer',
           'CheckBoxFieldRenderer', 'CheckBoxSet']

def iterable(item):
    try:
        iter(item)
    except:
        return False
    return True

class FieldRenderer(object):
    """
    This should be the super class of all Renderer classes.

    Renderers generate the html corresponding to a single Field,
    and are also responsible for deserializing form data into
    Python objects.

    Subclasses should override `render` and `deserialize`.
    See their docstrings for details.
    """
    def __init__(self, field):
        self.field = field
        assert isinstance(self.field, AbstractField)

    def name(self):
        """Name of rendered input element"""
        clsname = self.field.model.__class__.__name__
        pk = self.field.parent._bound_pk
        assert pk != ''
        def stringify_key(k):
            if k is None:
                return ''
            return unicode(k)
        if isinstance(pk, basestring) or not iterable(pk):
            pk_string = stringify_key(pk)
        else:
            # remember to use a delimiter that can be used in the DOM (specifically, no commas).
            # we don't have to worry about escaping the delimiter, since we never try to
            # deserialize the generated name.  All we care about is generating unique
            # names for a given model's domain.
            pk_string = u'_'.join([stringify_key(k) for k in pk])
        return u'%s-%s-%s' % (clsname, pk_string, self.field.name)
    name = property(name)

    def _value(self):
        """Submitted value, or field value if none"""
        if not self.field.is_readonly() and self._params is not None:
            v = self._serialized_value()
        else:
            v = None
        # empty field will be '' -- use default value there, too
        return v or self.field.value
    _value = property(_value)

    def render(self, **kwargs):
        """
        Render the field.  Use `self.name` to get a unique name for the
        input element and id.  `self._value` may also be useful if
        you are not rendering multiple input elements.
        """
        raise NotImplementedError()

    def render_readonly(self, **kwargs):
        """render a string representation of the field value"""
        value = self.field.raw_value
        if value is None:
            return ''
        if self.field.is_scalar_relation():
            q = self.field.parent.session.query(self.field.relation_type())
            v = q.get(value)
            return unicode(v)
        if isinstance(value, basestring):
            # FIXME this is a bad way to handle UnicodeEncodeError
            # FA need to implement a default charset and try to encode value
            # there
            return value
        if isinstance(value, list):
            return ', '.join([str(item) for item in value])
        return str(value)

    def _params(self):
        return self.field.parent.data
    _params = property(_params)

    def _serialized_value(self):
        """
        Returns the appropriate value to deserialize for field's
        datatype, from the user-submitted data.  Only called
        internally, so, if you are overriding `deserialize`,
        you can use or ignore `_serialized_value` as you please.

        This is broken out into a separate method so multi-input
        renderers can stitch their values back into a single one
        to have that can be handled by the default deserialize.

        Do not attempt to deserialize here; return value should be a
        string (corresponding to the output of `str` for your data
        type), or for a collection type, a a list of strings.

        The default _serialized_value returns the submitted value(s)
        in the input element corresponding to self.name.
        """
        if self.field.is_collection():
            return self._params.getall(self.name)
        return self._params.getone(self.name)

    def deserialize(self):
        """
        Turns the user-submitted data into a Python value.  (The raw
        data will be available in self.field.parent.data, or you
        can use `_serialized_value` if it is convenient.)  For SQLAlchemy
        collections, return a list of primary keys, and !FormAlchemy
        will take care of turning that into a list of objects.
        For manually added collections, return a list of values.

        You should only have to override this if you are using custom
        (e.g., Composite) types.
        """
        if self.field.is_collection():
            return [self._deserialize(subdata) for subdata in self._serialized_value()]
        return self._deserialize(self._serialized_value())

    def _deserialize(self, data):
        if isinstance(self.field.type, fatypes.Boolean):
            if data is not None:
                if data.lower() in ['1', 't', 'true', 'yes']: return True
                if data.lower() in ['0', 'f', 'false', 'no']: return False
        if data is None:
            return None
        if isinstance(self.field.type, fatypes.Integer):
            return validators.integer(data)
        if isinstance(self.field.type, fatypes.Float):
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

        if isinstance(self.field.type, fatypes.Date):
            return _date(data)
        if isinstance(self.field.type, fatypes.Time):
            return _time(data)
        if isinstance(self.field.type, fatypes.DateTime):
            data_date, data_time = data.split(' ')
            dt, tm = _date(data_date), _time(data_time)
            if dt is None and tm is None:
                return None
            elif dt is None or tm is None:
                raise validators.ValidationError('Incomplete datetime')
            return datetime.datetime(dt.year, dt.month, dt.day, tm.hour, tm.minute, tm.second)

        return data


class TextFieldRenderer(FieldRenderer):
    """render a field as a text field"""
    def length(self):
        return self.field.type.length
    length = property(length)

    def render(self, **kwargs):
        return h.text_field(self.name, value=self._value, maxlength=self.length, **kwargs)


class IntegerFieldRenderer(FieldRenderer):
    """render an integer as a text field"""
    def render(self, **kwargs):
        return h.text_field(self.name, value=self._value, **kwargs)


class FloatFieldRenderer(FieldRenderer):
    """render a float as a text field"""
    def render(self, **kwargs):
        return h.text_field(self.name, value=self._value, **kwargs)


class PasswordFieldRenderer(TextFieldRenderer):
    """Render a password field"""
    def render(self, **kwargs):
        return h.password_field(self.name, value=self._value, maxlength=self.length, **kwargs)
    def render_readonly(self):
        return '*'*6

class TextAreaFieldRenderer(FieldRenderer):
    """render a field as a textarea"""
    def render(self, **kwargs):
        if isinstance(kwargs.get('size'), tuple):
            kwargs['size'] = 'x'.join([str(i) for i in kwargs['size']])
        return h.text_area(self.name, content=self._value, **kwargs)


class HiddenFieldRenderer(FieldRenderer):
    """render a field as an hidden field"""
    def render(self, **kwargs):
        return h.hidden_field(self.name, value=self._value, **kwargs)
    def render_readonly(self):
        return ''


class CheckBoxFieldRenderer(FieldRenderer):
    """render a boolean value as checkbox field"""
    def render(self, **kwargs):
        return h.check_box(self.name, True, checked=self._value, **kwargs)
    def _serialized_value(self):
        if self.name not in self._params:
            return None
        return FieldRenderer._serialized_value(self)
    def deserialize(self):
        if self._serialized_value() is None:
            return False
        return FieldRenderer.deserialize(self)

class FileFieldRenderer(FieldRenderer):
    """render a file input field"""
    remove_label = _('Remove')
    def __init__(self, *args, **kwargs):
        FieldRenderer.__init__(self, *args, **kwargs)
        self._data = None # caches FieldStorage data
        self._filename = None

    def render(self, **kwargs):
        if self.field.value:
            checkbox_name = '%s--remove' % self.name
            return '%s %s %s' % (
                   h.file_field(self.name, **kwargs),
                   h.check_box(checkbox_name),
                   h.label(self.remove_label, for_=checkbox_name))
        else:
            return h.file_field(self.name, **kwargs)

    def get_size(self):
        value = self.field.raw_value
        if value is None:
            return 0
        return len(value)

    def readable_size(self):
        length = self.get_size()
        if length == 0:
            return '0 KB'
        if length <= 1024:
            return '1 KB'
        if length > 1048576:
            return '%0.02f MB' % (length / 1048576.0)
        return '%0.02f KB' % (length / 1024.0)

    def render_readonly(self, **kwargs):
        """
        render only the binary size in a human readable format but you can
        override it to whatever you want
        """
        return self.readable_size()

    def deserialize(self):
        data = FieldRenderer.deserialize(self)
        if isinstance(data, cgi.FieldStorage):
            if data.filename:
                # FieldStorage can only be read once so we need to cache the
                # value since FA call deserialize during validation and
                # synchronisation
                if self._data is None:
                    self._filename = data.filename
                    self._data = data.file.read()
                data = self._data
            else:
                data = None
        checkbox_name = '%s--remove' % self.name
        if not data and not self._params.has_key(checkbox_name):
            data = getattr(self.field.model, self.field.name)
        return data is not None and data or ''

# for when and/or is not safe b/c first might eval to false
def _ternary(condition, first, second):
    if condition:
        return first()
    return second()

class DateFieldRenderer(FieldRenderer):
    """Render a date field"""
    format = '%Y-%m-%d'
    def render_readonly(self, **kwargs):
        value = self.field.raw_value
        return value and value.strftime(self.format) or ''
    def _render(self, **kwargs):
        data = self._params
        import calendar
        month_options = [('Month', 'MM')] + [(calendar.month_name[i], str(i)) for i in xrange(1, 13)]
        day_options = [('Day', 'DD')] + [(i, str(i)) for i in xrange(1, 32)]
        mm_name = self.name + '__month'
        dd_name = self.name + '__day'
        yyyy_name = self.name + '__year'
        mm = _ternary((data is not None and mm_name in data), lambda: data[mm_name],  lambda: str(self._value and self._value.month))
        dd = _ternary((data is not None and dd_name in data), lambda: data[dd_name], lambda: str(self._value and self._value.day))
        # could be blank so don't use and/or construct
        if data is not None and yyyy_name in data:
            yyyy = data[yyyy_name]
        else:
            yyyy = str(self._value and self._value.year or 'YYYY')
        return h.select(mm_name, h.options_for_select(month_options, selected=mm), **kwargs) \
               + ' ' + h.select(dd_name, h.options_for_select(day_options, selected=dd), **kwargs) \
               + ' ' + h.text_field(yyyy_name, value=yyyy, maxlength=4, size=4, **kwargs)
    def render(self, **kwargs):
        return h.content_tag('span', self._render(**kwargs), id=self.name)

    def _serialized_value(self):
        return '-'.join([self._params.getone(self.name + '__' + subfield) for subfield in ['year', 'month', 'day']])


class TimeFieldRenderer(FieldRenderer):
    """Render a time field"""
    format = '%H:%M:%S'
    def render_readonly(self, **kwargs):
        value = self.field.raw_value
        return value and value.strftime(self.format) or ''
    def _render(self, **kwargs):
        data = self._params
        hour_options = ['HH'] + [(i, str(i)) for i in xrange(24)]
        minute_options = ['MM' ] + [(i, str(i)) for i in xrange(60)]
        second_options = ['SS'] + [(i, str(i)) for i in xrange(60)]
        hh_name = self.name + '__hour'
        mm_name = self.name + '__minute'
        ss_name = self.name + '__second'
        hh = _ternary((data is not None and hh_name in data), lambda: data[hh_name], lambda: str(self._value and self._value.hour))
        mm = _ternary((data is not None and mm_name in data), lambda: data[mm_name], lambda: str(self._value and self._value.minute))
        ss = _ternary((data is not None and ss_name in data), lambda: data[ss_name], lambda: str(self._value and self._value.second))
        return h.select(hh_name, h.options_for_select(hour_options, selected=hh), **kwargs) \
               + ':' + h.select(mm_name, h.options_for_select(minute_options, selected=mm), **kwargs) \
               + ':' + h.select(ss_name, h.options_for_select(second_options, selected=ss), **kwargs)
    def render(self, **kwargs):
        return h.content_tag('span', self._render(**kwargs), id=self.name)

    def _serialized_value(self):
        return ':'.join([self._params.getone(self.name + '__' + subfield) for subfield in ['hour', 'minute', 'second']])


class DateTimeFieldRenderer(DateFieldRenderer, TimeFieldRenderer):
    """Render a date time field"""
    format = '%Y-%m-%d %H:%M:%S'
    def render(self, **kwargs):
        return h.content_tag('span', DateFieldRenderer._render(self, **kwargs) + ' ' + TimeFieldRenderer._render(self, **kwargs), id=self.name)

    def _serialized_value(self):
        return DateFieldRenderer._serialized_value(self) + ' ' + TimeFieldRenderer._serialized_value(self)


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
    """render a field as radio"""
    widget = staticmethod(h.radio_button)
    format = '%(field)s%(label)s'
    
    def _serialized_value(self):
        if self.name not in self._params:
            return None
        return FieldRenderer._serialized_value(self)

    def _is_checked(self, choice_value):
        return self._value == choice_value

    def render(self, options, **kwargs):
        self.radios = []
        for i, (choice_name, choice_value) in enumerate(_extract_options(options)):
            choice_id = '%s_%i' % (self.name, i)
            radio = self.widget(self.name, choice_value, id=choice_id,
                                checked=self._is_checked(choice_value), **kwargs)
            label = h.content_tag('label', choice_name, for_=choice_id)
            self.radios.append(self.format % dict(field=radio,
                                                  label=label))
        return h.tag("br").join(self.radios)


class CheckBoxSet(RadioSet):
    widget = staticmethod(h.check_box)

    def _serialized_value(self):
        if self.name not in self._params:
            return []
        return FieldRenderer._serialized_value(self)

    def _is_checked(self, choice_value):
        return choice_value in self._value


class SelectFieldRenderer(FieldRenderer):
    """render a field as select"""
    def render(self, options, **kwargs):
        selected = kwargs.get('selected', None) or self._value
        return h.select(self.name, h.options_for_select(options, selected=selected), **kwargs)


def _pk_one_column(instance, column):
    try:
        attr = getattr(instance, column.key)
    except AttributeError:
        # FIXME: this is not clean but the only way i've found to retrieve the
        # real attribute name of the primary key.
        # This is needed when you use something like:
        #    id = Column('UGLY_NAMED_ID', primary_key=True)
        # It's a *really* needed feature
        cls = instance.__class__
        for k in instance._sa_class_manager.keys():
            props = getattr(cls, k).property
            if hasattr(props, 'columns'):
                if props.columns[0] is column:
                    attr = getattr(instance, k)
                    break
    return attr

def _pk(instance):
    # Return the value of this instance's primary key, suitable for passing to Query.get().  
    # Will be a tuple if PK is multicolumn.
    try:
        columns = class_mapper(type(instance)).primary_key
    except InvalidRequestError:
        return None
    if len(columns) == 1:
        return _pk_one_column(instance, columns[0])
    return tuple([_pk_one_column(instance, column) for column in columns])


# see http://code.activestate.com/recipes/364469/ for explanation.
# 2.6 provides ast.literal_eval, but requiring 2.6 is a bit of a stretch for now.
import compiler
class _SafeEval(object):
    def visit(self, node,**kw):
        cls = node.__class__
        meth = getattr(self,'visit'+cls.__name__,self.default)
        return meth(node, **kw)
            
    def default(self, node, **kw):
        for child in node.getChildNodes():
            return self.visit(child, **kw)
            
    visitExpression = default
    
    def visitConst(self, node, **kw):
        return node.value

    def visitTuple(self,node, **kw):
        return tuple(self.visit(i) for i in node.nodes)
        
    def visitList(self,node, **kw):
        return [self.visit(i) for i in node.nodes]

def _simple_eval(source):
    """like 2.6's ast.literal_eval, but only does constants, lists, and tuples, for serialized pk eval"""
    walker = _SafeEval()
    ast = compiler.parse(source, 'eval')
    return walker.visit(ast)


def _query_options(L):
    """
    Return a list of tuples of `(item description, item pk)`
    for each item in the iterable L, where `item description`
    is the result of str(item) and `item pk` is the item's primary key.
    """
    return [(unicode(item), _pk(item)) for item in L]


def _normalized_options(options):
    """
    If `options` is an SA query or an iterable of SA instances, it will be
    turned into a list of `(item description, item value)` pairs. Otherwise, a
    copy of the original options will be returned with no further validation.
    """
    if isinstance(options, Query):
        options = options.all()
    i = iter(options)
    try:
        first = i.next()
    except StopIteration:
        return []
    try:
        class_mapper(type(first))
    except:
        return list(options)
    return _query_options(options)


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
        try:
            wrapper._renderer = copy(self._renderer)
        except TypeError: # 2.4 support
            # it's a lambda, safe to just use same referende
            pass
        if hasattr(wrapper._renderer, 'field'):
            wrapper._renderer.field = wrapper
        return wrapper

    def requires_label(self):
        return not isinstance(self.renderer, HiddenFieldRenderer)
    requires_label = property(requires_label)

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
        if self.is_readonly():
            return True

        self.errors = []

        try:
            value = self._deserialize()
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

    def is_readonly(self):
        """True iff this Field is in readonly mode"""
        return self.modifier=='readonly'

    def model(self):
        return self.parent.model
    model = property(model)

    def _modified(self, **kwattrs):
        # return a copy of self, with the given attributes modified
        copied = deepcopy(self)
        for attr, value in kwattrs.iteritems():
            setattr(copied, attr, value)
        return copied
    def with_renderer(self, r):
        """
        Return a copy of this Field, with a different renderer.
        Used for one-off renderer changes; if you want to change the
        renderer for all instances of a Field type, modify
        FieldSet.default_renderers instead.
        """
        return self._modified(_renderer=r)
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
        field.render_opts = {}
        return field
    def textarea(self, size=None):
        """
        Render the field as a textarea.  Size must be a string
        (`"25x10"`) or tuple (`25, 10`).
        """
        field = deepcopy(self)
        field._renderer = lambda: self.parent.default_renderers['textarea']
        if size:
            field.render_opts = {'size': size}
        return field
    def radio(self, options=None):
        """Render the field as a set of radio buttons."""
        field = deepcopy(self)
        field._renderer = lambda: self.parent.default_renderers['radio']
        if options is None:
            options = self.render_opts.get('options')
        else:
            options = _normalized_options(options)
        field.render_opts = {'options': options}
        return field
    def checkbox(self, options=None):
        """Render the field as a set of checkboxes."""
        field = deepcopy(self)
        field._renderer = lambda: field.parent.default_renderers['checkbox']
        if options is None:
            options = self.render_opts.get('options')
        else:
            options = _normalized_options(options)
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
        else:
            options = _normalized_options(options)
        field.render_opts = {'multiple': multiple, 'options': options}
        if multiple:
            field.render_opts['size'] = size
        return field
    def reset(self):
        """
        Return the field with all configuration changes reverted.
        """
        return deepcopy(self.parent._fields[self.name])

    def _get_renderer(self):
        for t in self.parent.default_renderers:
            if not isinstance(t, basestring) and isinstance(self.type, t):
                return self.parent.default_renderers[t]
        raise TypeError(
                'No renderer found for field %s. '
                'Type %s as no default renderer' % (self.name, self.type))

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
        opts['readonly'] = opts.get('readonly') or self.is_readonly()
        opts['disabled'] = opts.get('disabled') or self.modifier=='disabled'
        if (isinstance(self.type, fatypes.Boolean)
            and not opts.get('options')
            and self.renderer.__class__ in [self.parent.default_renderers['dropdown'], self.parent.default_renderers['radio']]):
            opts['options'] = [('Yes', True), ('No', False)]
        if self.is_readonly():
            return self.renderer.render_readonly(**opts)
        return self.renderer.render(**opts)

    def render_readonly(self, **html_options):
        """
        Render this Field as HTML for read only mode.

        `html_options` are not used by the default template, but are
        provided to make more customization possible in custom templates
        """
        opts = dict(self.render_opts)
        opts.update(html_options)
        return self.renderer.render_readonly(**opts)

    def _deserialize(self):
        return self.renderer.deserialize()

class Field(AbstractField):
    """
    A manually-added form field
    """
    def __init__(self, name=None, type=fatypes.String, value=None):
        """
          * `name`: field name
          * `type`: data type, from formalchemy.types (Boolean, Integer, String, etc.),
            or a custom type for which you have added a renderer.
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
        if not self.is_readonly() and self.parent.data is not None:
            v = self._deserialize()
            if v is not None:
                return v
        try:
            # this is NOT the same as getattr -- getattr will return the class's
            # value for the attribute name, which for a manually added Field will
            # be the Field object.  So force looking in the instance __dict__ only.
            return self.model.__dict__[self.name]
        except KeyError:
            pass
        if callable(self._value):
            return self._value(self.model)
        return self._value
    value = property(value)

    def key(self):
        return self.name
    key = property(key)

    def is_collection(self):
        return self.render_opts.get('multiple', False) or isinstance(self.renderer, self.parent.default_renderers['checkbox'])
    
    def is_relation(self):
        return False

    def is_scalar_relation(self):
        return False

    def raw_value(self):
        return self.value
    raw_value = property(raw_value)

    def sync(self):
        """Set the attribute's value in `model` to the value given in `data`"""
        if not self.is_readonly():
            self._value = self._deserialize()

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
        if not self.is_collection() and [c for c in self._columns if not c.nullable]:
            self.validators.append(validators.required)

    def is_raw_foreign_key(self):
        try:
            return _foreign_keys(self._property.columns[0])
        except AttributeError:
            return False
        
    def is_composite_foreign_key(self):
        return len(self._columns) > 1 and not [c for c in self._columns if not _foreign_keys(c)]

    def is_pk(self):
        return bool([c for c in self._columns if c.primary_key])

    def type(self):
        if self.is_composite():
            # this is a little confusing -- we need to return an _instance_ of
            # the correct type, which for composite values will be the value
            # itself. SA should probably have called .type something
            # different, or just not instantiated them...
            return self.parent.model
        if len(self._columns) > 1:
            return None # may have to be more accurate here
        return self._columns[0].type
    type = property(type)

    def _columns(self):
        if isinstance(self._impl, ScalarObjectAttributeImpl):
            # If the attribute is a foreign key, return the Column that this
            # attribute is mapped from -- e.g., .user -> .user_id.
            return _foreign_keys(self._property)
        elif isinstance(self._impl, ScalarAttributeImpl) or self._impl.__class__.__name__ in ('ProxyImpl', '_ProxyImpl'): # 0.4 compatibility: ProxyImpl is a one-off class for each synonym, can't import it
            # normal property, mapped to a single column from the main table
            return self._property.columns
        else:
            # collection -- use the mapped class's PK
            assert isinstance(self._impl, CollectionAttributeImpl), self._impl.__class__
            return self._property.mapper.primary_key
    _columns = property(_columns)

    def key(self):
        """
        The name of the attribute in the class.
        
        >>> from formalchemy.tests import FieldSet, Order
        >>> fs = FieldSet(Order)
        >>> print fs.user.key
        user
        """
        return self._impl.key
    key = property(key)
    
    def _column_name(self):
        return '_'.join([c.name for c in self._columns])
    _column_name = property(_column_name)

    def name(self):
        """
        The name of the form input. usually the same as the key, except for
        multi-valued SA relation properties. For example, for order.user,
        name will be 'user_id' (assuming that is indeed the name of the foreign
        key to users), but for user.orders, name will be 'orders'.

        >>> from formalchemy.tests import FieldSet, Order
        >>> fs = FieldSet(Order)
        >>> print fs.user.name
        user_id
        """
        if self.is_collection() or self.is_composite() or not hasattr(self.model, self._column_name):
            return self.key
        return self._column_name
    name = property(name)

    def is_collection(self):
        """True iff this is a multi-valued (one-to-many or many-to-many) SA relation"""
        return isinstance(self._impl, CollectionAttributeImpl)

    def is_composite(self):
        return isinstance(self._property, CompositeProperty)

    def is_relation(self):
        """True iff this field represents a mapped SA relation"""
        return self.is_scalar_relation() or self.is_collection()

    def is_scalar_relation(self):
        """True iff this is the 'one' end of a one-to-many relation"""
        return isinstance(self._impl, ScalarObjectAttributeImpl)

    def relation_type(self):
        """
        The type of object in the collection (e.g., `User`).
        Calling this is only valid when `is_relation()` is True.
        """
        return self._property.mapper.class_

    def value(self):
        """
        The value of this Field: use the corresponding value in the bound `data`,
        if any; otherwise, use the value in the bound `model`.  If there is still no
        value, use the default defined on the corresponding `Column`.

        For collections,
        a list of the primary key values of the items in the collection is returned.
        """
        if not self.is_readonly() and self.parent.data is not None:
            v = self._deserialize()
        else:
            try:
                v = getattr(self.model, self.name)
            except AttributeError:
                v = getattr(self.model, self.key)
        if self.is_collection():
            return [_pk(item) for item in v]
        if v is not None:
            return v
        
        if len(self._columns) == 1 and  self._columns[0].default:
            arg = self._columns[0].default.arg
            if callable(arg):
                # callables often depend on the current time, e.g. datetime.now or the equivalent SQL function.
                # these are meant to be the value *at insertion time*, so it's not strictly correct to
                # generate a value at form-edit time.
                pass
            else:
                return arg
        return None
    value = property(value)

    def raw_value(self):
        """
        raw value from model.  different from `.value`, because for reference types,
        `.value` will return the foreign key ID.  This will return the actual object 
        referenced instead.
        """
        return getattr(self.model, self.name)
    raw_value = property(raw_value)

    def sync(self):
        """Set the attribute's value in `model` to the value given in `data`"""
        if not self.is_readonly():
            setattr(self.model, self.name, self._deserialize())

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

    # todo? add .options method (for html_options)

    def render(self, **html_options):
        if self.is_relation() and not self.render_opts.get('options'):
            # todo 2.0 this does not handle primaryjoin (/secondaryjoin) alternate join conditions
            fk_cls = self.relation_type()
            fk_pk = class_mapper(fk_cls).primary_key[0]
            q = self.parent.session.query(fk_cls).order_by(fk_pk)
            self.render_opts['options'] = _query_options(q)
            logger.debug('options for %s are %s' % (self.name, self.render_opts['options']))
        if self.is_collection() and isinstance(self.renderer, self.parent.default_renderers['dropdown']):
            self.render_opts['multiple'] = True
            if 'size' not in self.render_opts:
                self.render_opts['size'] = 5
        return AbstractField.render(self, **html_options)

    def _get_renderer(self):
        if self.is_relation():
            return self.parent.default_renderers['dropdown']
        return AbstractField._get_renderer(self)
    
    def _deserialize(self):
        # for multicolumn keys, we turn the string into python via _simple_eval; otherwise,
        # the key is just the raw deserialized value (which is already an int, etc., as necessary)
        if len(self._columns) > 1:
            python_pk = _simple_eval
        else:
            python_pk = lambda st: st
            
        if self.is_collection():
            return [self.query(self.relation_type()).get(python_pk(pk)) for pk in self.renderer.deserialize()]
        if self.is_composite_foreign_key():
            return self.query(self.relation_type()).get(python_pk(self.renderer.deserialize()))
        return self.renderer.deserialize()
