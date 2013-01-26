# Copyright (C) 2007 Alexandre Conrad, alexandre (dot) conrad (at) gmail (dot) com
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import cgi
import logging
logger = logging.getLogger('formalchemy.' + __name__)

from copy import copy, deepcopy
import datetime
import warnings

from sqlalchemy.orm.interfaces import MANYTOMANY
from sqlalchemy.orm.interfaces import ONETOMANY
from sqlalchemy.orm import class_mapper, Query
from sqlalchemy.orm.attributes import ScalarAttributeImpl, ScalarObjectAttributeImpl, CollectionAttributeImpl
from sqlalchemy.orm.properties import CompositeProperty, ColumnProperty
try:
    from sqlalchemy import exc as sqlalchemy_exceptions
except ImportError:
    from sqlalchemy import exceptions as sqlalchemy_exceptions
from sqlalchemy.orm import object_session
from formalchemy import helpers as h
from formalchemy import fatypes, validators
from formalchemy.exceptions import FieldNotFoundError
from formalchemy import config
from formalchemy.i18n import get_translator
from formalchemy.i18n import _

__all__ = ['Field', 'FieldRenderer',
           'TextFieldRenderer', 'TextAreaFieldRenderer',
           'PasswordFieldRenderer', 'HiddenFieldRenderer',
           'DateFieldRenderer', 'TimeFieldRenderer',
           'DateTimeFieldRenderer',
           'CheckBoxFieldRenderer', 'CheckBoxSet',
           'deserialize_once']



########################## RENDERER STUFF ############################



def _stringify(k, null_value=u''):
    if k is None:
        return null_value
    if isinstance(k, str):
        return unicode(k, config.encoding)
    elif isinstance(k, unicode):
        return k
    elif hasattr(k, '__unicode__'):
        return unicode(k)
    elif isinstance(k, datetime.timedelta):
        return '%s.%s' % (k.days, k.seconds)
    else:
        return unicode(str(k), config.encoding)

def _htmlify(k, null_value=u''):
    if hasattr(k, '__html__'):
        try:
            return h.literal(k.__html__())
        except TypeError:
            # not callable. skipping
            pass
    return _stringify(k, null_value)

class _NoDefault(object):
    def __repr__(self):
        return '<NoDefault>'
NoDefault = _NoDefault()
del _NoDefault

def deserialize_once(func):
    """Simple deserialization caching decorator.

    To be used on a Renderer object's `deserialize` function, to cache it's
    result while it's being called once for ``validate()`` and another time
    when doing ``sync()``.
    """
    def cache(self, *args, **kwargs):
        if hasattr(self, '_deserialization_result'):
            return self._deserialization_result

        self._deserialization_result = func(self, *args, **kwargs)

        return self._deserialization_result
    return cache

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

    @property
    def name(self):
        """Name of rendered input element.

        The `name` of a field will always look like:
          [fieldset_prefix-]ModelName-[pk]-fieldname

        The fieldset_prefix is defined when instantiating the
        `FieldSet` object, by passing the `prefix=` keyword argument.

        The `ModelName` is taken by introspection from the model
        passed in at that same moment.

        The `pk` is the primary key of the object being edited.
        If you are creating a new object, then the `pk` is an
        empty string.

        The `fieldname` is, well, the field name.

        .. note::
         This method as the direct consequence that you can not `create`
         two objects of the same class, using the same FieldSet, on the
         same page. You can however, create more than one object
         of a certain class, provided that you create multiple FieldSet
         instances and pass the `prefix=` keyword argument.

         Otherwise, FormAlchemy deals very well with editing multiple
         existing objects of same/different types on the same page,
         without any name clash. Just be careful with multiple object
         creation.

        When creating your own Renderer objects, use `self.name` to
        get the field's `name` HTML attribute, both when rendering
        and deserializing.
        """
        clsname = self.field.model.__class__.__name__
        pk = self.field.parent._bound_pk
        assert pk != ''
        if isinstance(pk, basestring) or not hasattr(pk, '__iter__'):
            pk_string = _stringify(pk)
        else:
            # remember to use a delimiter that can be used in the DOM (specifically, no commas).
            # we don't have to worry about escaping the delimiter, since we never try to
            # deserialize the generated name.  All we care about is generating unique
            # names for a given model's domain.
            pk_string = u'_'.join([_stringify(k) for k in pk])

        components = dict(model=clsname, pk=pk_string, name=self.field.name)
        name = self.field.parent._format % components
        if self.field.parent._prefix is not None:
            return u'%s-%s' % (self.field.parent._prefix, name)
        return name

    @property
    def value(self):
        """
        Submitted value, or field value converted to string.
        Return value is always either None or a string.
        """
        if not self.field.is_readonly() and self.params is not None:
            # submitted value.  do not deserialize here since that requires valid data, which we might not have
            try:
                v = self._serialized_value()
            except FieldNotFoundError, e:
                v = None
        else:
            v = None
        # empty field will be '' -- use default value there, too
        if v:
            return v

        value = self.field.model_value
        if value is None:
            return None
        if self.field.is_collection:
            return [self.stringify_value(v) for v in value]
        else:
            return self.stringify_value(value)

    @property
    def _value(self):
        warnings.warn('FieldRenderer._value is deprecated. Use '\
                          'FieldRenderer.value instead')
        return self.value

    @property
    def raw_value(self):
        """return fields field.raw_value (mean real objects, not ForeignKeys)
        """
        return self.field.raw_value

    @property
    def request(self):
        """return the ``request`` bound to the
        :class:`~formalchemy.forms.FieldSet`` during
        :func:`~formalchemy.forms.FieldSet.bind`"""
        return self.field.parent._request

    def get_translator(self, **kwargs):
        """return a GNUTranslations object in the most convenient way
        """
        if 'F_' in kwargs:
            return kwargs.pop('F_')
        if 'lang' in kwargs:
            lang = kwargs.pop('lang')
        else:
            lang = 'en'
        return get_translator(lang=lang, request=self.request)

    def render(self, **kwargs):
        """
        Render the field.  Use `self.name` to get a unique name for the
        input element and id.  `self.value` may also be useful if
        you are not rendering multiple input elements.

        When rendering, you can verify `self.errors` to know
        if you are rendering a new form, or re-displaying a form with
        errors. Knowing that, you could select the data either from
        the model, or the web form submission.
        """
        raise NotImplementedError()

    def render_readonly(self, **kwargs):
        """render a string representation of the field value"""
        value = self.raw_value
        if value is None:
            return ''
        if isinstance(value, list):
            return h.literal(', ').join([self.stringify_value(item, as_html=True) for item in value])
        if isinstance(value, unicode):
            return value
        return self.stringify_value(value, as_html=True)

    @property
    def params(self):
        """This gives access to the POSTed data, as received from
        the web user. You should call `.getone`, or `.getall` to
        retrieve a single value or multiple values for a given
        key.

        For example, when coding a renderer, you'd use:

        .. sourcecode:: py

           vals = self.params.getall(self.name)

        to catch all the values for the renderer's form entry.
        """
        return self.field.parent.data

    @property
    def _params(self):
        warnings.warn('FieldRenderer._params is deprecated. Use '\
                          'FieldRenderer.params instead')
        return self.params

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
        type), or for a collection type, a a list of strings,
        or None if no value was submitted for this renderer.

        The default _serialized_value returns the submitted value(s)
        in the input element corresponding to self.name.
        """
        try:
            if self.field.is_collection:
                return self.params.getall(self.name)
            return self.params.getone(self.name)
        except KeyError:
            raise FieldNotFoundError('%s not found in %r' % (self.name, self.params))

    def deserialize(self):
        """Turns the user-submitted data into a Python value.

        The raw data received from the web can be accessed via
        `self.params`. This dict-like object usually accepts the
        `getone()` and `getall()` method calls.

        For SQLAlchemy
        collections, return a list of primary keys, and !FormAlchemy
        will take care of turning that into a list of objects.
        For manually added collections, return a list of values.

        You will need to override this in a child Renderer object
        if you want to mangle the data from your web form, before
        it reaches your database model. For example, if your render()
        method displays a select box filled with items you got from a
        CSV file or another source, you will need to decide what to do
        with those values when it's time to save them to the database
        -- or is this field going to determine the hashing algorithm
        for your password ?.

        This function should return the value that is going to be
        assigned to the model *and* used in the place of the model
        value if there was an error with the form.

        .. note::
         Note that this function will be called *twice*, once when
         the fieldset is `.validate()`'d -- with it's value only tested,
         and a second time when the fieldset is `.sync()`'d -- and it's
         value assigned to the model. Also note that deserialize() can
         also raise a ValidationError() exception if it finds some
         errors converting it's values.

        If calling this function twice poses a problem to your logic, for
        example, if you have heavy database queries, or temporary objects
        created in this function, consider using the ``deserialize_once``
        decorator, provided using:

        .. sourcecode:: py

          from formalchemy.fields import deserialize_once

          @deserialize_once
          def deserialize(self):
              ... my stuff ...
              return calculated_only_once

        Finally, you should only have to override this if you are using custom
        (e.g., Composite) types.
        """
        if self.field.is_collection:
            return [self._deserialize(subdata) for subdata in self._serialized_value()]
        return self._deserialize(self._serialized_value())

    def _deserialize(self, data):
        if isinstance(self.field.type, fatypes.Boolean):
            if isinstance(data, bool):
                 return data
            if data is not None:
                if data.lower() in ['1', 't', 'true', 'yes']: return True
                if data.lower() in ['0', 'f', 'false', 'no']: return False
        if data is None or data == self.field._null_option[1]:
            return None
        if isinstance(self.field.type, fatypes.Interval):
            return datetime.timedelta(validators.float_(data, self))
        if isinstance(self.field.type, fatypes.Integer):
            return validators.integer(data, self)
        if isinstance(self.field.type, fatypes.Float):
            return validators.float_(data, self)
        if isinstance(self.field.type, fatypes.Numeric):
            if self.field.type.asdecimal:
                return validators.decimal_(data, self)
            else:
                return validators.float_(data, self)

        def _date(data):
            if isinstance(data, datetime.date):
                return data
            if data == 'YYYY-MM-DD' or data == '-MM-DD' or not data.strip():
                return None
            try:
                return datetime.date(*[int(st) for st in data.split('-')])
            except:
                raise validators.ValidationError('Invalid date')
        def _time(data):
            if isinstance(data, datetime.time):
                return data
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
            if isinstance(data, datetime.datetime):
                return data
            if 'Z' in data:
                data = data.strip('Z')
            if 'T' in data:
                data_date, data_time = data.split('T')
            elif ' ' in data:
                data_date, data_time = data.split(' ')
            else:
                raise validators.ValidationError('Incomplete datetime: %s' % data)
            dt, tm = _date(data_date), _time(data_time)
            if dt is None and tm is None:
                return None
            elif dt is None or tm is None:
                raise validators.ValidationError('Incomplete datetime')
            return datetime.datetime(dt.year, dt.month, dt.day, tm.hour, tm.minute, tm.second)

        return data

    def stringify_value(self, v, as_html=False):
        if as_html:
            return _htmlify(v, null_value=self.field._null_option[1])
        return _stringify(v, null_value=self.field._null_option[1])

    def __repr__(self):
        return '<%s for %r>' % (self.__class__.__name__, self.field)

class EscapingReadonlyRenderer(FieldRenderer):
    """
    In readonly mode, html-escapes the output of the default renderer
    for this field type.  (Escaping is not performed by default because
    it is sometimes useful to have the renderer include raw html in its
    output.  The FormAlchemy admin app extension for Pylons uses this,
    for instance.)
    """
    def __init__(self, field):
        FieldRenderer.__init__(self, field)
        self._renderer = field._get_renderer()(field)

    def render(self, **kwargs):
        return self._renderer.render(**kwargs)

    def render_readonly(self, **kwargs):
        return h.HTML(self._renderer.render_readonly(**kwargs))


class TextFieldRenderer(FieldRenderer):
    """render a field as a text field"""
    @property
    def length(self):
        return self.field.type.length

    def render(self, **kwargs):
        return h.text_field(self.name, value=self.value, maxlength=self.length, **kwargs)


class IntegerFieldRenderer(FieldRenderer):
    """render an integer as a text field"""
    def render(self, **kwargs):
        return h.text_field(self.name, value=self.value, **kwargs)


class FloatFieldRenderer(FieldRenderer):
    """render a float as a text field"""
    def render(self, **kwargs):
        return h.text_field(self.name, value=self.value, **kwargs)

class IntervalFieldRenderer(FloatFieldRenderer):
    """render an interval as a text field"""

    def _deserialize(self, data):
        value = FloatFieldRenderer._deserialize(self, data)
        if isinstance(value, (float, int)):
            return datetime.timedelta(value)
        return value

class PasswordFieldRenderer(TextFieldRenderer):
    """Render a password field"""
    def render(self, **kwargs):
        return h.password_field(self.name, value=self.value, maxlength=self.length, **kwargs)
    def render_readonly(self):
        return '*' * 6

class TextAreaFieldRenderer(FieldRenderer):
    """render a field as a textarea"""
    def render(self, **kwargs):
        if isinstance(kwargs.get('size'), tuple):
            kwargs['size'] = 'x'.join([str(i) for i in kwargs['size']])
        return h.text_area(self.name, content=self.value, **kwargs)


class CheckBoxFieldRenderer(FieldRenderer):
    """render a boolean value as checkbox field"""
    def render(self, **kwargs):
        value = self.value or ''
        return h.check_box(self.name, True,
                           checked=_simple_eval(value.capitalize()),
                           **kwargs)
    def _serialized_value(self):
        if self.name not in self.params:
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
        if self.field.model_value:
            checkbox_name = '%s--remove' % self.name
            return h.literal('%s %s %s') % (
                   h.file_field(self.name, **kwargs),
                   h.check_box(checkbox_name),
                   h.label(self.remove_label, for_=checkbox_name))
        else:
            return h.file_field(self.name, **kwargs)

    def get_size(self):
        value = self.raw_value
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
        if not data and not self.params.has_key(checkbox_name):
            data = getattr(self.field.model, self.field.name)
        return data is not None and data or ''

class DateFieldRenderer(FieldRenderer):
    """Render a date field"""
    @property
    def format(self):
        return config.date_format
    @property
    def edit_format(self):
        return config.date_edit_format
    def render_readonly(self, **kwargs):
        value = self.raw_value
        return value and value.strftime(self.format) or ''
    def _render(self, **kwargs):
        data = self.params
        value = self.field.model_value
        F_ = self.get_translator(**kwargs)
        month_options = [(F_('Month'), 'MM')] + [(F_('month_%02i' % i), str(i)) for i in xrange(1, 13)]
        day_options = [(F_('Day'), 'DD')] + [(i, str(i)) for i in xrange(1, 32)]
        mm_name = self.name + '__month'
        dd_name = self.name + '__day'
        yyyy_name = self.name + '__year'
        is_date_type = isinstance(value, (datetime.datetime, datetime.date, datetime.time))
        values = []
        for key, default in (('month', 'MM'), ('day', 'DD')):
            name = self.name + '__' + key
            v = default
            if data is not None and name in data:
                v = data[name]
            if v.isdigit():
                pass
            elif is_date_type:
                v = getattr(value, key)
            values.append(v)
        mm, dd = values
        # could be blank so don't use and/or construct
        if data is not None and yyyy_name in data:
            yyyy = data[yyyy_name]
        else:
            yyyy = str(self.field.model_value and self.field.model_value.year or 'YYYY')
        selects = dict(
                m=h.select(mm_name, [mm], month_options, **kwargs),
                d=h.select(dd_name, [dd], day_options, **kwargs),
                y=h.text_field(yyyy_name, value=yyyy, maxlength=4, size=4, **kwargs))
        value = [selects.get(l) for l in self.edit_format.split('-')]
        return h.literal('\n').join(value)
    def render(self, **kwargs):
        return h.content_tag('span', self._render(**kwargs), id=self.name)

    def _serialized_value(self):
        return '-'.join([self.params.getone(self.name + '__' + subfield) for subfield in ['year', 'month', 'day']])

class TimeFieldRenderer(FieldRenderer):
    """Render a time field"""
    format = '%H:%M:%S'
    def is_time_type(self):
        return isinstance(self.field.model_value, (datetime.datetime, datetime.date, datetime.time))
    def render_readonly(self, **kwargs):
        value = self.raw_value
        return isinstance(value, datetime.time) and value.strftime(self.format) or ''
    def _render(self, **kwargs):
        data = self.params
        value = self.field.model_value
        hour_options = ['HH'] + [str(i) for i in xrange(24)]
        minute_options = ['MM' ] + [str(i) for i in xrange(60)]
        second_options = ['SS'] + [str(i) for i in xrange(60)]
        hh_name = self.name + '__hour'
        mm_name = self.name + '__minute'
        ss_name = self.name + '__second'
        is_time_type = isinstance(value, (datetime.datetime, datetime.date, datetime.time))
        values = []
        for key, default in (('hour', 'HH'), ('minute', 'MM'), ('second', 'SS')):
            name = self.name + '__' + key
            v = default
            if data is not None and name in data:
                v = data[name]
            if v.isdigit():
                pass
            elif is_time_type:
                v = getattr(value, key)
            values.append(v)
        hh, mm, ss = values
        return h.literal(':').join([
                    h.select(hh_name, [hh], hour_options, **kwargs),
                    h.select(mm_name, [mm], minute_options, **kwargs),
                    h.select(ss_name, [ss], second_options, **kwargs)])
    def render(self, **kwargs):
        return h.content_tag('span', self._render(**kwargs), id=self.name)

    def _serialized_value(self):
        return ':'.join([self.params.getone(self.name + '__' + subfield) for subfield in ['hour', 'minute', 'second']])


class DateTimeFieldRenderer(DateFieldRenderer, TimeFieldRenderer):
    """Render a date time field"""
    format = '%Y-%m-%d %H:%M:%S'
    def render(self, **kwargs):
        return h.content_tag('span', DateFieldRenderer._render(self, **kwargs) + h.literal(' ') + TimeFieldRenderer._render(self, **kwargs), id=self.name)

    def _serialized_value(self):
        return DateFieldRenderer._serialized_value(self) + ' ' + TimeFieldRenderer._serialized_value(self)


class EmailFieldRenderer(FieldRenderer):
    '''
    Render a HTML5 email input field
    '''

    def render(self, **kwargs):
        return h.text_field(self.name, value=self.value, type='email', **kwargs)


class UrlFieldRenderer(FieldRenderer):
    '''
    Render a HTML5 url input field
    '''

    def render(self, **kwargs):
        return h.text_field(self.name, value=self.value, type='url', **kwargs)


class NumberFieldRenderer(IntegerFieldRenderer):
    '''
    Render a HTML5 number input field
    '''

    def render(self, **kwargs):
        return h.text_field(self.name, value=self.value, type='number', **kwargs)


class RangeFieldRenderer(FieldRenderer):
    '''
    Render a HTML5 range input field
    '''

    def render(self, **kwargs):
        return h.text_field(self.name, value=self.value, type='range', **kwargs)


class HTML5DateFieldRenderer(FieldRenderer):
    '''
    Render a HTML5 date input field
    '''

    def render(self, **kwargs):
        return h.text_field(self.name, value=self.value, type='date', **kwargs)

class HTML5DateTimeFieldRenderer(FieldRenderer):
    '''
    Render a HTML5 datetime input field
    '''

    def render(self, **kwargs):
        return h.text_field(self.name, value=self.value, type='datetime', **kwargs)

class LocalDateTimeFieldRenderer(FieldRenderer):
    '''
    Render a HTML5 datetime-local input field.
    '''

    def render(self, **kwargs):
        return h.text_field(self.name, value=self.value, type='datetime-local', **kwargs)


class MonthFieldRender(FieldRenderer):
    '''
    Render a HTML5 month input field.
    '''

    def render(self, **kwargs):
        return h.text_field(self.name, value=self.value, type='month', **kwargs)


class WeekFieldRenderer(FieldRenderer):
    '''
    Render a HTML5 week input field.
    '''

    def render(self, **kwargs):
        return h.text_field(self.name, value=self.value, type='week', **kwargs)


class HTML5TimeFieldRenderer(FieldRenderer):
    '''
    Render a HTML5 time input field.
    '''

    def render(self, **kwargs):
        return h.text_field(self.name, value=self.value, type='time', **kwargs)

class ColorFieldRenderer(FieldRenderer):
    '''
    Render a HTML5 color input field.
    '''

    def render(self, **kwargs):
        return h.text_field(self.name, value=self.value, type='color', **kwargs)


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
        if self.name not in self.params:
            return None
        return FieldRenderer._serialized_value(self)

    def _is_checked(self, choice_value, value=NoDefault):
        if value is NoDefault:
            value = self.value
        return value == _stringify(choice_value)

    def render(self, options, **kwargs):
        value = self.value
        self.radios = []
        if callable(options):
            options = options(self.field.parent)
        for i, (choice_name, choice_value) in enumerate(_extract_options(options)):
            choice_id = '%s_%i' % (self.name, i)
            radio = self.widget(self.name, choice_value, id=choice_id,
                                checked=self._is_checked(choice_value, value),
                                **kwargs)
            label = h.label(choice_name, for_=choice_id)
            self.radios.append(h.literal(self.format % dict(field=radio,
                                                            label=label)))
        return h.tag("br").join(self.radios)


class CheckBoxSet(RadioSet):
    widget = staticmethod(h.check_box)

    def _serialized_value(self):
        if self.name not in self.params:
            return []
        return FieldRenderer._serialized_value(self)

    def _is_checked(self, choice_value, value=NoDefault):
        if value is NoDefault:
            value = self.value
        if value is None:
            value = []
        return _stringify(choice_value) in value


class SelectFieldRenderer(FieldRenderer):
    """render a field as select"""
    def _serialized_value(self):
        if self.name not in self.params:
            if self.field.is_collection:
                return []
            return None
        return FieldRenderer._serialized_value(self)

    def render(self, options, **kwargs):
        if callable(options):
            L = _normalized_options(options(self.field.parent))
            if not self.field.is_required() and not self.field.is_collection:
                L.insert(0, self.field._null_option)
        else:
            L = list(options)
        if len(L) > 0:
            if len(L[0]) == 2:
                L = [(k, self.stringify_value(v)) for k, v in L]
            else:
                L = [_stringify(k) for k in L]
        return h.select(self.name, self.value, L, **kwargs)

    def render_readonly(self, options=None, **kwargs):
        """render a string representation of the field value.
           Try to retrieve a value from `options`
        """
        if not options or self.field.is_scalar_relation:
            return FieldRenderer.render_readonly(self)

        value = self.raw_value
        if value is None:
            return ''

        if callable(options):
            L = _normalized_options(options(self.field.parent))
        else:
            L = list(options)

        if len(L) > 0:
            if len(L[0]) == 2:
                L = [(v, k) for k, v in L]
            else:
                L = [(k, _stringify(k)) for k in L]
        D = dict(L)
        if isinstance(value, list):
            return u', '.join([_stringify(D.get(item, item)) for item in value])
        return _stringify(D.get(value, value))


class HiddenFieldRenderer(FieldRenderer):
    """render a field as an hidden field"""
    def render(self, **kwargs):
        return h.hidden_field(self.name, value=self.value, **kwargs)
    def render_readonly(self):
        return ''

def HiddenFieldRendererFactory(cls):
    """A factory to generate a new class to hide an existing renderer"""
    class Renderer(cls, HiddenFieldRenderer):
        def render(self, **kwargs):
            html = super(Renderer, self).render(**kwargs)
            return h.content_tag('div', html, style="display:none;")
        def render_readonly(self):
            return ''
    attrs = dict(__doc__="""Hidden %s renderer""" % cls.__name__)
    renderer = type('Hidden%s' % cls.__name__, (Renderer,), attrs)
    return renderer


HiddenDateFieldRenderer = HiddenFieldRendererFactory(DateFieldRenderer)
HiddenTimeFieldRenderer = HiddenFieldRendererFactory(TimeFieldRenderer)
HiddenDateTimeFieldRenderer = HiddenFieldRendererFactory(DateTimeFieldRenderer)




################## FIELDS STUFF ####################



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
    except sqlalchemy_exceptions.InvalidRequestError:
        # try to get pk from model attribute
        if hasattr(instance, '_pk'):
            return getattr(instance, '_pk', None) or None
        return None
    if len(columns) == 1:
        return _pk_one_column(instance, columns[0])
    return tuple([_pk_one_column(instance, column) for column in columns])


# see http://code.activestate.com/recipes/364469/ for explanation.
# 2.6 provides ast.literal_eval, but requiring 2.6 is a bit of a stretch for now.
import compiler
class _SafeEval(object):
    def visit(self, node, **kw):
        cls = node.__class__
        meth = getattr(self, 'visit' + cls.__name__, self.default)
        return meth(node, **kw)

    def default(self, node, **kw):
        for child in node.getChildNodes():
            return self.visit(child, **kw)

    visitExpression = default

    def visitName(self, node, **kw):
        if node.name in ['True', 'False', 'None']:
            return eval(node.name)

    def visitConst(self, node, **kw):
        return node.value

    def visitTuple(self, node, **kw):
        return tuple(self.visit(i) for i in node.nodes)

    def visitList(self, node, **kw):
        return [self.visit(i) for i in node.nodes]

def _simple_eval(source):
    """like 2.6's ast.literal_eval, but only does constants, lists, and tuples, for serialized pk eval"""
    if source == '':
        return None
    walker = _SafeEval()
    ast = compiler.parse(source, 'eval')
    return walker.visit(ast)


def _query_options(L):
    """
    Return a list of tuples of `(item description, item pk)`
    for each item in the iterable L, where `item description`
    is the result of str(item) and `item pk` is the item's primary key.
    """
    return [(_stringify(item), _pk(item)) for item in L]


def _normalized_options(options):
    """
    If `options` is an SA query or an iterable of SA instances, it will be
    turned into a list of `(item description, item value)` pairs. Otherwise, a
    copy of the original options will be returned with no further validation.
    """
    if isinstance(options, Query):
        options = options.all()
    if callable(options):
        return options
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

    Methods taking an `options` parameter will accept several ways of
    specifying those options:

    - an iterable of SQLAlchemy objects; `str()` of each object will be the description, and the primary key the value
    - a SQLAlchemy query; the query will be executed with `all()` and the objects returned evaluated as above
    - an iterable of (description, value) pairs
    - a dictionary of {description: value} pairs

    Options can be "chained" indefinitely because each modification returns a new
    :mod:`Field <formalchemy.fields>` instance, so you can write::

    >>> from formalchemy.tests import FieldSet, User
    >>> fs = FieldSet(User)
    >>> fs.append(Field('foo').dropdown(options=[('one', 1), ('two', 2)]).radio())

    or::

    >>> fs.configure(options=[fs.name.label('Username').readonly()])

    """
    _null_option = (u'None', u'')
    _valide_options = [
            'validate', 'renderer', 'hidden', 'required', 'readonly',
            'null_as', 'label', 'multiple', 'options', 'validators',
            'size', 'instructions', 'metadata', 'html']

    def __init__(self, parent, name=None, type=fatypes.String, **kwattrs):
        # the FieldSet (or any ModelRenderer) owning this instance
        self.parent = parent
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
        self._readonly = False
        # label to use for the rendered field.  autoguessed if not specified by .label()
        self.label_text = None
        # optional attributes to pass to renderers
        self.html_options = {}
        # True iff this Field is a primary key
        self.is_pk = False
        # True iff this Field is a raw foreign key
        self.is_raw_foreign_key = False
        # Field metadata, for customization
        self.metadata = {}
        self.name = name
        self.type = type

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

    @property
    def requires_label(self):
        return not isinstance(self.renderer, HiddenFieldRenderer)

    def query(self, *args, **kwargs):
        """Perform a query in the parent's session"""
        if self.parent.session:
            session = self.parent.session
        else:
            session = object_session(self.model)
        if session:
            return session.query(*args, **kwargs)
        raise Exception(("No session found.  Either bind a session explicitly, "
                         "or specify relation options manually so FormAlchemy doesn't try to autoload them."))

    def _validate(self):
        if self.is_readonly():
            return True

        self.errors = []

        try:
            # Call renderer.deserialize(), because the deserializer can
            # also raise a ValidationError
            value = self._deserialize()
        except validators.ValidationError, e:
            self.errors.append(e.message)
            return False

        L = list(self.validators)
        if self.is_required() and validators.required not in L:
            L.append(validators.required)
        for validator in L:
            if (not (hasattr(validator, 'accepts_none') and validator.accepts_none)) and value is None:
                continue
            try:
                validator(value, self)
            except validators.ValidationError, e:
                self.errors.append(e.message)
            except TypeError:
                warnings.warn(DeprecationWarning('Please provide a field argument to your %r validator. Your validator will break in FA 1.5' % validator))
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
        return self._readonly

    @property
    def model(self):
        return self.parent.model

    def _modified(self, **kwattrs):
        # return a copy of self, with the given attributes modified
        copied = deepcopy(self)
        for attr, value in kwattrs.iteritems():
            setattr(copied, attr, value)
        return copied

    def set(self, **kwattrs):
        """
        Sets different properties on the Field object. In contrast to the
        other methods that tweak a Field, this one changes thing
        IN-PLACE, without creating a new object and returning it.
        This is the behavior for the other methods like ``readonly()``,
        ``required()``, ``with_html()``, ``with_metadata``,
        ``with_renderer()``, ``with_null_as()``, ``label()``,
        ``hidden()``, ``validate()``, etc...

        Allowed attributes are:

         * ``validate`` - append one single validator
         * ``validators`` - appends a list of validators
         * ``renderer`` - sets the renderer used (``.with_renderer(val)``
           equiv.)
         * ``hidden`` - marks a field as hidden (changes the renderer)
         * ``required`` - adds the default 'required' validator to the field
         * ``readonly`` - sets the readonly attribute (``.readonly(val)``
           equiv.)
         * ``null_as`` - sets the 'null_as' attribute (``.with_null_as(val)``
           equiv.)
         * ``label`` - sets the label (``.label(val)`` equiv.)
         * ``multiple`` - marks the field as a multi-select (used by some
           renderers)
         * ``options`` - sets `.render_opts['options']` (for selects and similar
           fields, used by some renderers)
         * ``size`` - sets render_opts['size'] with this val (normally an
           attribute to ``textarea()``, ``dropdown()``, used by some renderers)
         * ``instructions`` - shortcut to update `metadata['instructions']`
         * ``metadata`` - dictionary that `updates` the ``.metadata`` attribute
         * ``html`` - dictionary that updates the ``.html_options`` attribute
           (``.with_html()`` equiv.)

        NOTE: everything in ``.render_opts``, updated with everything in
        ``.html_options`` will be passed as keyword arguments to the `render()`
        function of the Renderer set for the field.

        Example::

            >>> field = Field('myfield')
            >>> field.set(label='My field', renderer=SelectFieldRenderer,
            ...           options=[('Value', 1)],
            ...           validators=[lambda x: x, lambda y: y])
            AttributeField(myfield)
            >>> field.label_text
            'My field'
            >>> field.renderer
            <SelectFieldRenderer for AttributeField(myfield)>

        """
        attrs = kwattrs.keys()
        mapping = dict(renderer='_renderer',
                       readonly='_readonly',
                       null_as='_null_option',
                       label='label_text')
        for attr in attrs:
            value = kwattrs.pop(attr)
            if attr == 'validate':
                self.validators.append(value)
            elif attr == 'validators':
                self.validators.extend(value)
            elif attr == 'metadata':
                self.metadata.update(value)
            elif attr == 'html':
                self.html_options.update(value)
            elif attr == 'instructions':
                self.metadata['instructions'] = value
            elif attr == 'required':
                if value:
                    if validators.required not in self.validators:
                        self.validators.append(validators.required)
                else:
                    if validators.required in self.validators:
                        self.validators.remove(validators.required)
            elif attr == 'hidden':
                if isinstance(self.type, fatypes.Date):
                    renderer = HiddenDateFieldRenderer
                elif isinstance(self.type, fatypes.Time):
                    renderer = HiddenTimeFieldRenderer
                elif isinstance(self.type, fatypes.DateTime):
                    renderer = HiddenDateTimeFieldRenderer
                else:
                    renderer = HiddenFieldRenderer
                self._renderer = renderer
            elif attr in 'attrs':
                self.render_opts.update(value)
            elif attr in mapping:
                attr = mapping.get(attr)
                setattr(self, attr, value)
            elif attr in ('multiple', 'options', 'size'):
                if attr == 'options' and value is not None:
                    value = _normalized_options(value)
                self.render_opts[attr] = value
            else:
                raise ValueError('Invalid argument %s' % attr)
        return self

    def with_null_as(self, option):
        """Render null as the given option tuple of text, value."""
        return self._modified(_null_option=option)
    def with_renderer(self, renderer):
        """
        Return a copy of this Field, with a different renderer.
        Used for one-off renderer changes; if you want to change the
        renderer for all instances of a Field type, modify
        FieldSet.default_renderers instead.
        """
        return self._modified(_renderer=renderer)
    def bind(self, parent):
        """Return a copy of this Field, bound to a different parent"""
        return self._modified(parent=parent)
    def with_metadata(self, **attrs):
        """Attach some metadata attributes to the Field, to be used by
        conditions in templates.

        Example usage:

          >>> test = Field('test')
          >>> field = test.with_metadata(instructions='use this widget this way')
          ...

        And further in your templates you can verify:

          >>> 'instructions' in field.metadata
          True

        and display the content in a <span> or something.
        """
        new_attr = self.metadata.copy()
        new_attr.update(attrs)
        return self._modified(metadata=new_attr)
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
        Convenience method for `validate(validators.required)`. By
        default, NOT NULL columns are required. You can only add
        required-ness, not remove it.
        """
        return self.validate(validators.required)
    def with_html(self, **html_options):
        """
        Give some HTML options to renderer.

        Trailing underscore (_) characters will be stripped. For example,
        you might want to add a `class` attribute to your checkbox. You
        would need to specify `.options(class_='someclass')`.

        For WebHelpers-aware people: those parameters will be passed to
        the `text_area()`, `password()`, `text()`, etc.. webhelpers.

        NOTE: Those options can override generated attributes and can mess
              the `sync` calls, or `label`-tag associations (if you change
              `name`, or `id` for example).  Use with caution.
        """
        new_opts = copy(self.html_options)
        for k, v in html_options.iteritems():
            new_opts[k.rstrip('_')] = v
        return self._modified(html_options=new_opts)
    def label(self, text=NoDefault):
        """Get or set the label for the field. If a value is provided then change
        the label associated with this field.  By default, the field name is
        used, modified for readability (e.g., 'user_name' -> 'User name').
        """
        if text is NoDefault:
            if self.label_text is not None:
                text = self.label_text
            else:
                text = self.parent.prettify(self.key)
            if text:
                F_ = get_translator(request=self.parent._request)
                return h.escape_once(F_(text))
            else:
                return ''
        return self._modified(label_text=text)
    def label_tag(self, **html_options):
        """return the <label /> tag for the field."""
        html_options.update(for_=self.renderer.name)
        if 'class_' in html_options:
            html_options['class_'] += self.is_required() and ' field_req' or ' field_opt'
        else:
            html_options['class_'] = self.is_required() and 'field_req' or 'field_opt'
        return h.content_tag('label', self.label(), **html_options)
    def attrs(self, **kwargs):
        """update ``render_opts``"""
        self.render_opts.update(kwargs)
        return self._modified(render_opts=self.render_opts)
    def readonly(self, value=True):
        """
        Render the field readonly.

        By default, this marks a field to be rendered as read-only.
        Setting the `value` argument to `False` marks the field as editable.
        """
        return self._modified(_readonly=value)
    def hidden(self):
        """Render the field hidden.  (Value only, no label.)"""
        if isinstance(self.type, fatypes.Date):
            renderer = HiddenDateFieldRenderer
        elif isinstance(self.type, fatypes.Time):
            renderer = HiddenTimeFieldRenderer
        elif isinstance(self.type, fatypes.DateTime):
            renderer = HiddenDateTimeFieldRenderer
        else:
            renderer = HiddenFieldRenderer
        return self._modified(_renderer=renderer, render_opts={})
    def password(self):
        """Render the field as a password input, hiding its value."""
        field = deepcopy(self)
        field._renderer = lambda f: f.parent.default_renderers['password']
        field.render_opts = {}
        return field
    def textarea(self, size=None):
        """
        Render the field as a textarea.  Size must be a string
        (`"25x10"`) or tuple (`25, 10`).
        """
        field = deepcopy(self)
        field._renderer = lambda f: f.parent.default_renderers['textarea']
        if size:
            field.render_opts = {'size': size}
        return field
    def radio(self, options=None):
        """Render the field as a set of radio buttons."""
        field = deepcopy(self)
        field._renderer = lambda f: f.parent.default_renderers['radio']
        if options is None:
            options = self.render_opts.get('options')
        else:
            options = _normalized_options(options)
        field.render_opts = {'options': options}
        return field
    def checkbox(self, options=None):
        """Render the field as a set of checkboxes."""
        field = deepcopy(self)
        field._renderer = lambda f: f.parent.default_renderers['checkbox']
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
        field._renderer = lambda f: f.parent.default_renderers['dropdown']
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

    #==========================================================================
    # HTML5 specific input types
    #==========================================================================

    def date(self):
        '''
        Render the field as a HTML5 date input type.
        '''
        field = deepcopy(self)
        field._renderer = lambda f: f.parent.default_renderers['date']
        return field

    def datetime(self):
        '''
        Render the field as a HTML5 datetime input type.
        '''
        field = deepcopy(self)
        field._renderer = lambda f: f.parent.default_renderers['datetime']
        return field

    def datetime_local(self):
        '''
        Render the field as a HTML5 datetime-local input type.
        '''
        field = deepcopy(self)
        field._renderer = lambda f: f.parent.default_renderers['date']
        return field

    def month(self):
        '''
        Render the field as a HTML5 month input type.
        '''
        field = deepcopy(self)
        field._renderer = lambda f: f.parent.default_renderers['month']
        return field

    def week(self):
        '''
        Render the field as a HTML5 week input type.
        '''
        field = deepcopy(self)
        field._renderer = lambda f: f.parent.default_renderers['week']
        return field

    def time(self):
        '''
        Render the field as a HTML5 time input type.
        '''
        field = deepcopy(self)
        field._renderer = lambda f: f.parent.default_renderers['time']
        return field

    def color(self):
        '''
        Render the field as a HTML5 color input type.
        '''
        field = deepcopy(self)
        field._renderer = lambda f: f.parent.default_renderers['color']
        return field

    def range(self, min_=None, max_=None, step=None, value=None):
        '''
        Render the field as a HTML5 range input type, starting at `min_`,
        ending at `max_`, with legal increments every `step` distance.  The
        default is set by `value`.
        '''
        field = deepcopy(self)
        field._renderer = lambda f: f.parent.default_renderers['range']
        field.render_opts = {}
        if min_:
            field.render_opts["min"] = min_
        if max_:
            field.render_opts["max"] = max_
        if step:
            field.render_opts["step"] = step
        if value:
            field.render_opts["value"] = value
        return field

    def number(self, min_=None, max_=None, step=None, value=None):
        '''
        Render the field as a HTML5 number input type, starting at `min_`,
        ending at `max_`, with legal increments every `step` distance.  The
        default is set by `value`.
        '''
        field = deepcopy(self)
        field._renderer = lambda f: f.parent.default_renderers['number']
        field.render_opts = {}
        if min_:
            field.render_opts["min"] = min_
        if max_:
            field.render_opts["max"] = max_
        if step:
            field.render_opts["step"] = step
        if value:
            field.render_opts["value"] = value
        return field

    def url(self):
        '''
        Render the field as a HTML5 url input type.
        '''
        field = deepcopy(self)
        field._renderer = lambda f: f.parent.default_renderers['url']
        return field

    def email(self):
        '''
        Render the field as a HTML5 email input type.
        '''
        field = deepcopy(self)
        field._renderer = lambda f: f.parent.default_renderers['email']
        return field

    def _get_renderer(self):
        for t in self.parent.default_renderers:
            if not isinstance(t, basestring) and type(self.type) is t:
                return self.parent.default_renderers[t]
        for t in self.parent.default_renderers:
            if not isinstance(t, basestring) and isinstance(self.type, t):
                return self.parent.default_renderers[t]
        raise TypeError(
                'No renderer found for field %s. '
                'Type %s as no default renderer' % (self.name, self.type))

    @property
    def renderer(self):
        if self._renderer is None:
            self._renderer = self._get_renderer()
        try:
            self._renderer = self._renderer(self)
        except TypeError:
            pass
        if not isinstance(self._renderer, FieldRenderer):
            # must be a Renderer class.  instantiate.
            self._renderer = self._renderer(self)
        return self._renderer

    def _get_render_opts(self):
        """
        Calculate the final options dict to be sent to renderers.
        """
        # Use options from internally set render_opts
        opts = dict(self.render_opts)
        # Override with user-specified options (with .with_html())
        opts.update(self.html_options)
        return opts

    def render(self):
        """
        Render this Field as HTML.
        """
        if self.is_readonly():
            return self.render_readonly()

        opts = self._get_render_opts()

        if (isinstance(self.type, fatypes.Boolean)
            and not opts.get('options')
            and self.renderer.__class__ in [self.parent.default_renderers['dropdown'], self.parent.default_renderers['radio']]):
            opts['options'] = [('Yes', True), ('No', False)]
        return self.renderer.render(**opts)

    def render_readonly(self):
        """
        Render this Field as HTML for read only mode.
        """
        return self.renderer.render_readonly(**self._get_render_opts())

    def _pkify(self, value):
        """return the PK for value, if applicable"""
        return value

    @property
    def value(self):
        """
        The value of this Field: use the corresponding value in the bound `data`,
        if any; otherwise, use the value in the bound `model`.  For SQLAlchemy models,
        if there is still no value, use the default defined on the corresponding `Column`.

        For SQLAlchemy collections,
        a list of the primary key values of the items in the collection is returned.

        Invalid form data will cause an error to be raised.  Controllers should thus validate first.
        Renderers should thus never access .value; use .model_value instead.
        """
        # TODO add ._validated flag to save users from themselves?
        if not self.is_readonly() and self.parent.data is not None:
            v = self._deserialize()
            if v is not None:
                return self._pkify(v)
        return self.model_value

    @property
    def model_value(self):
        """
        raw value from model, transformed if necessary for use as a form input value.
        """
        raise NotImplementedError()

    @property
    def raw_value(self):
        """
        raw value from model.  different from `.model_value` in SQLAlchemy fields, because for reference types,
        `.model_value` will return the foreign key ID.  This will return the actual object
        referenced instead.
        """
        raise NotImplementedError()

    def _deserialize(self):
        return self.renderer.deserialize()

class Field(AbstractField):
    """
    A manually-added form field
    """
    def __init__(self, name=None, type=fatypes.String, value=None, **kwattrs):
        """
        Create a new Field object.

        - `name`:
              field name

        - `type=types.String`:
              data type, from formalchemy.types (Integer, Float, String,
              LargeBinary, Boolean, Date, DateTime, Time) or a custom type

        - `value=None`:
              default value.  If value is a callable, it will be passed the current
              bound model instance when the value is read.  This allows creating a
              Field whose value depends on the model once, then binding different
              instances to it later.

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
        self.name = self.key = name
        self._value = value
        self.is_relation = False
        self.is_scalar_relation = False
        self.set(**kwattrs)

    def set(self, **kwattrs):
        if 'value' in kwattrs:
            self._value = kwattrs.pop('value')
        return AbstractField.set(self, **kwattrs)

    @property
    def model_value(self):
        return self.raw_value

    @property
    def is_collection(self):
        if isinstance(self.type, (fatypes.List, fatypes.Set)):
            return True
        return self.render_opts.get('multiple', False) or isinstance(self.renderer, self.parent.default_renderers['checkbox'])

    @property
    def raw_value(self):
        try:
            # this is NOT the same as getattr -- getattr will return the class's
            # value for the attribute name, which for a manually added Field will
            # be the Field object.  So force looking in the instance __dict__ only.
            return self.model.__dict__[self.name]
        except (KeyError, AttributeError):
            pass
        if callable(self._value):
            return self._value(self.model)
        return self._value

    def sync(self):
        """Set the attribute's value in `model` to the value given in `data`"""
        if not self.is_readonly():
            self._value = self._deserialize()

    def __repr__(self):
        return 'AttributeField(%s)' % self.name

    def __unicode__(self):
        return self.render_readonly()

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
        """
            >>> from formalchemy.tests import FieldSet, Order
            >>> fs = FieldSet(Order)
            >>> print fs.user.key
            user

            >>> print fs.user.name
            user_id
        """
        AbstractField.__init__(self, parent)
        # we rip out just the parts we care about from InstrumentedAttribute.
        # impl is the AttributeImpl.  So far all we care about there is ".key,"
        # which is the name of the attribute in the mapped class.
        self._impl = instrumented_attribute.impl
        # property is the PropertyLoader which handles all the interesting stuff.
        # mapper, columns, and foreign keys are all located there.
        self._property = instrumented_attribute.property

        # True iff this is a multi-valued (one-to-many or many-to-many) SA relation
        self.is_collection = isinstance(self._impl, CollectionAttributeImpl)

        # True iff this is the 'one' end of a one-to-many relation
        self.is_scalar_relation = isinstance(self._impl, ScalarObjectAttributeImpl)

        # True iff this field represents a mapped SA relation
        self.is_relation = self.is_scalar_relation or self.is_collection

        self.is_composite = isinstance(self._property, CompositeProperty)

        _columns = self._columns

        self.is_pk = bool([c for c in self._columns if c.primary_key])

        self.is_raw_foreign_key = bool(isinstance(self._property, ColumnProperty) and _foreign_keys(self._property.columns[0]))

        self.is_composite_foreign_key = len(_columns) > 1 and not [c for c in _columns if not _foreign_keys(c)]

        if self.is_composite:
            # this is a little confusing -- we need to return an _instance_ of
            # the correct type, which for composite values will be the value
            # itself. SA should probably have called .type something
            # different, or just not instantiated them...
            self.type = self._property.composite_class.__new__(self._property.composite_class)
        elif len(_columns) > 1:
            self.type = None # may have to be more accurate here
        else:
            self.type = _columns[0].type

        self.key = self._impl.key
        self._column_name = '_'.join([c.name for c in _columns])

        # The name of the form input. usually the same as the key, except for
        # single-valued SA relation properties. For example, for order.user,
        # name will be 'user_id' (assuming that is indeed the name of the foreign
        # key to users), but for user.orders, name will be 'orders'.
        if self.is_collection or self.is_composite or not hasattr(self.model, self._column_name):
            self.name = self.key
        else:
            self.name = self._column_name

        # smarter default "required" value
        if not self.is_collection and not self.is_readonly() and [c for c in _columns if not c.nullable]:
            self.validators.append(validators.required)

        info = dict([(str(k), v) for k, v in self.info.items() if k in self._valide_options])
        if self.is_relation and 'label' not in info:
            m = self._property.mapper.class_
            label = getattr(m, '__label__', None)
            if self._property.direction in (MANYTOMANY, ONETOMANY):
                label = getattr(m, '__plural__', label)
            if label:
                info['label'] = label
        self.set(**info)

    @property
    def info(self):
        """return the best information from SA's Column.info"""
        info = None

        if self.is_relation:
            pairs = self._property.local_remote_pairs
            if len(pairs):
                for pair in reversed(pairs):
                    for col in pair:
                        if col.table in self._property.parent.tables and not col.primary_key:
                            return getattr(col, 'info', None)
                        elif col.table in self._property.mapper.tables:
                            if col.primary_key:
                                if self._property.direction == MANYTOMANY:
                                    return getattr(col, 'info', None)
                            else:
                                parent_info = getattr(col, 'info', {})
                                info = {}
                                for k, v in parent_info.items():
                                    if k.startswith('backref_'):
                                        info[k[8:]] = v
                                return info
        else:
            try:
                col = getattr(self.model.__table__.c, self.key)
            except AttributeError:
                return {}
            else:
                return getattr(col, 'info', None)
        return {}

    def is_readonly(self):
        from sqlalchemy.sql.expression import _Label
        return AbstractField.is_readonly(self) or isinstance(self._columns[0], _Label)

    @property
    def _columns(self):
        if self.is_scalar_relation:
            # If the attribute is a foreign key, return the Column that this
            # attribute is mapped from -- e.g., .user -> .user_id.
            return _foreign_keys(self._property)
        elif isinstance(self._impl, ScalarAttributeImpl) or self._impl.__class__.__name__ in ('ProxyImpl', '_ProxyImpl'): # 0.4 compatibility: ProxyImpl is a one-off class for each synonym, can't import it
            # normal property, mapped to a single column from the main table
            prop = getattr(self._property, '_proxied_property', None)
            if prop is None:
                prop = self._property
            return prop.columns
        else:
            # collection -- use the mapped class's PK
            assert self.is_collection, self._impl.__class__
            return self._property.mapper.primary_key

    def relation_type(self):
        """
        The type of object in the collection (e.g., `User`).
        Calling this is only valid when `is_relation` is True.
        """
        return self._property.mapper.class_

    def _pkify(self, value):
        """return the PK for value, if applicable"""
        if value is None:
            return None
        if self.is_collection:
            return [_pk(item) for item in value]
        if self.is_relation:
            return _pk(value)
        return value

    @property
    def model_value(self):
        return self._pkify(self.raw_value)

    @property
    def raw_value(self):
        if self.is_scalar_relation:
            v = getattr(self.model, self.key)
        else:
            try:
                v = getattr(self.model, self.name)
            except AttributeError:
                v = getattr(self.model, self.key)
        if v is not None:
            return v

        _columns = self._columns
        if len(_columns) == 1 and  _columns[0].default:
            try:
                from sqlalchemy.sql.expression import Function
            except ImportError:
                from sqlalchemy.sql.expression import _Function as Function
            arg = _columns[0].default.arg
            if callable(arg) or isinstance(arg, Function):
                # callables often depend on the current time, e.g. datetime.now or the equivalent SQL function.
                # these are meant to be the value *at insertion time*, so it's not strictly correct to
                # generate a value at form-edit time.
                pass
            else:
                return arg
        return None

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

    def render(self):
        if self.is_readonly():
            return self.render_readonly()
        if self.is_relation and self.render_opts.get('options') is None:
            if self.is_required() or self.is_collection:
                self.render_opts['options'] = []
            else:
                self.render_opts['options'] = [self._null_option]
            # todo 2.0 this does not handle primaryjoin (/secondaryjoin) alternate join conditions
            q = self.query(self.relation_type())
            order_by = self._property.order_by
            if order_by:
                if not isinstance(order_by, list):
                    order_by = [order_by]
                q = q.order_by(*order_by)
            self.render_opts['options'] += _query_options(q)
            logger.debug('options for %s are %s' % (self.name, self.render_opts['options']))
        if self.is_collection and isinstance(self.renderer, self.parent.default_renderers['dropdown']):
            self.render_opts['multiple'] = True
            if 'size' not in self.render_opts:
                self.render_opts['size'] = 5
        return AbstractField.render(self)

    def _get_renderer(self):
        if self.is_relation:
            return self.parent.default_renderers['dropdown']
        return AbstractField._get_renderer(self)

    def _deserialize(self):
        # for multicolumn keys, we turn the string into python via _simple_eval; otherwise,
        # the key is just the raw deserialized value (which is already an int, etc., as necessary)
        if len(self._columns) > 1:
            python_pk = _simple_eval
        else:
            python_pk = lambda st: st

        if self.is_collection:
            return [self.query(self.relation_type()).get(python_pk(pk)) for pk in self.renderer.deserialize()]
        if self.is_composite_foreign_key:
            return self.query(self.relation_type()).get(python_pk(self.renderer.deserialize()))
        return self.renderer.deserialize()
