# -*- coding: utf-8 -*-
__doc__ = """This module provides an experimental subclass of
:class:`~formalchemy.forms.FieldSet` to support zope.schema_'s schema.  `Simple
validation`_ is supported. `Invariant`_ is not supported.

.. _zope.schema: http://pypi.python.org/pypi/zope.schema
.. _simple validation: http://pypi.python.org/pypi/zope.schema#simple-usage
.. _invariant: http://pypi.python.org/pypi/zope.schema#schema-validation

Available fields
================

Not all fields are supported. You can use TextLine, Text, Int, Bool, Float,
Date, Datetime, Time.

Usage
=====

Here is a simple example. First we need a schema::

    >>> class IPet(interface.Interface):
    ...     name = schema.Text(
    ...         title=u'Name',
    ...         required=True)
    ...     type = schema.TextLine(
    ...         title=u'Type',
    ...         required=True)
    ...     age = schema.Int(min=1)
    ...     owner = schema.TextLine(
    ...         title=u'Owner')
    ...     birthdate = schema.Date(title=u'Birth date')

Initialize FieldSet with schema::

    >>> fs = FieldSet(IPet)

Create a class to store values. If your class does not implement the form interface the FieldSet will generate an adapter for you::

    >>> class Pet(FlexibleDict):pass
    >>> p = Pet(name='dewey', type='cat', owner='gawel')
    >>> fs = fs.bind(p)

Fields are aware of schema attributes::

    >>> fs.name.is_required()
    True

We can use the form::

    >>> print fs.render().strip() #doctest: +ELLIPSIS
    <div>
      <label class="field_req" for="Pet--name">Name</label>
      <textarea id="Pet--name" name="Pet--name">dewey</textarea>
    </div>
    ...
    <div>
      <label class="field_req" for="Pet--birthdate">Birth date</label>
      <span id="Pet--birthdate"><select id="Pet--birthdate__month" name="Pet--birthdate__month"><option value="MM">Month</option>
    <option value="1">January</option>
    <option value="2">February</option>
    ...

Ok, let's assume that validation and syncing works::

    >>> fs.configure(include=[fs.name])
    >>> fs.rebind(p, data={'Pet--name':'minou'})
    >>> fs.validate()
    True
    >>> fs.sync()
    >>> fs.name.value
    'minou'
    >>> p.name
    'minou'

    >>> fs.configure(include=[fs.age])
    >>> fs.rebind(p, data={'Pet--age':'-1'})
    >>> fs.validate()
    False
    >>> fs.age.errors
    [u'Value is too small']

Look nice !

"""
from formalchemy.forms import FieldSet as BaseFieldSet
from formalchemy.tables import Grid as BaseGrid
from formalchemy.fields import Field as BaseField
from formalchemy.fields import _stringify
from formalchemy.base import SimpleMultiDict
from formalchemy import fields
from formalchemy import validators
from formalchemy import fatypes
from sqlalchemy.util import OrderedDict
from datetime import datetime
from zope import schema
from zope.schema import interfaces
from zope import interface

FIELDS_MAPPING = {
        schema.TextLine: fatypes.Unicode,
        schema.Text: fatypes.Unicode,
        schema.Int: fatypes.Integer,
        schema.Bool: fatypes.Boolean,
        schema.Float: fatypes.Float,
        schema.Date: fatypes.Date,
        schema.Datetime: fatypes.DateTime,
        schema.Time: fatypes.Time,
    }

class FlexibleModel(object):
    """A flexible object to easy adapt most python classes:

    .. sourcecode:: python

        >>> obj = FlexibleModel(owner='gawel')
        >>> obj.owner == obj.get('owner') == obj['owner'] == 'gawel'
        True

    """
    def __init__(self, context=None, **kwargs):
        if context is None:
            self._context = dict(**kwargs)
        else:
            self._context = context

    def __getattr__(self, attr):
        """flexible __getattr__. also used for __getitem__ and get"""
        if hasattr(self._context, attr):
            return getattr(self._context, attr, None)
        elif self._is_dict or isinstance(self._context, dict):
            return self._context.get(attr)
        raise AttributeError('%r as no attribute %s' % (self._context, attr))
    __getitem__ = get = __getattr__

    def __setattr__(self, attr, value):
        """flexible __getattr__"""
        if attr.startswith('_'):
            return object.__setattr__(self, attr, value)
        elif not self._is_dict and hasattr(self._context, attr):
            setattr(self._context, attr, value)
        elif self._is_dict or isinstance(self._context, dict):
            self._context[attr] = value
        else:
            raise AttributeError('%r as no attribute %s' % (self._context, attr))
    def __repr__(self):
        return '<%s for %s>' % (self.__class__.__name__, repr(self._context))

class FlexibleDict(FlexibleModel, dict):
    """like FlexibleModel but inherit from dict:

    .. sourcecode:: python

        >>> obj = FlexibleModel(owner='gawel')
        >>> obj.owner == obj.get('owner') == obj['owner'] == 'gawel'
        True
        >>> isinstance(obj, dict)
        True

    """
    _is_dict = True

_model_registry = {}

def gen_model(iface, klass=None, dict_like=False):
    """return a new FlexibleModel factory who provide iface:

    .. sourcecode:: python

        >>> class ITitle(interfaces.Interface):
        ...     title = schema.TextLine(title=u'title')

        >>> factory = gen_model(ITitle)
        >>> obj = factory()
        >>> ITitle.providedBy(obj)
        True

    """
    if klass:
        if not hasattr(klass, '__name__'):
            klass = klass.__class__
        name = class_name = klass.__name__
    else:
        class_name = None
        name = iface.__name__[1:]
    adapter = _model_registry.get((iface.__name__, class_name), None)
    if adapter is not None:
        return adapter
    new_klass = type('%sAdapter' % name, (FlexibleModel,), dict(_is_dict=dict_like))
    def adapter(context=None, **kwargs):
        adapted = new_klass(context=context, **kwargs)
        interface.directlyProvides(adapted, [iface])
        return adapted
    _model_registry[(iface.__name__, class_name)] = adapter
    return adapter

class Field(BaseField):
    """Field aware of zope schema. See :class:`formalchemy.fields.AbstractField` for full api."""
    def value(self):
        if not self.is_readonly() and self.parent.data is not None:
            v = self._deserialize()
            if v is not None:
                return v
        return getattr(self.model, self.name)
    value = property(value)

    def raw_value(self):
        try:
            return getattr(self.model, self.name)
        except (KeyError, AttributeError):
            pass
        if callable(self._value):
            return self._value(self.model)
        return self._value
    raw_value = property(raw_value)

    def _validate(self):
        if self.is_readonly():
            return True

        valide = BaseField._validate(self)
        if not valide:
            return False

        value = self._deserialize()

        if isinstance(self.type, fatypes.Unicode) and not isinstance(value, unicode):
            value = _stringify(value)

        field = self.parent.iface[self.name]
        bound = field.bind(self.model)
        try:
            bound.validate(value)
        except schema.ValidationError, e:
            self.errors.append(e.doc())

        return not self.errors

    def sync(self):
        """Set the attribute's value in `model` to the value given in `data`"""
        if not self.is_readonly():
            setattr(self.model, self.name, self._deserialize())


class FieldSet(BaseFieldSet):
    """FieldSet aware of zope schema. See :class:`formalchemy.forms.FieldSet` for full api."""
    auto_adapt = True
    auto_gen = True
    def __init__(self, model, session=None, data=None, prefix=None):
        self._fields = OrderedDict()
        self._render_fields = OrderedDict()
        self.model = self.session = None
        self.prefix = prefix
        self.model = model
        self.readonly = False
        self.focus = True
        self._errors = []
        self.validator = None
        self.iface = model
        focus = True
        for name, field in schema.getFieldsInOrder(model):
            klass = field.__class__
            try:
                t = FIELDS_MAPPING[klass]
            except KeyError:
                raise NotImplementedError('%s is not mapped to a type' % klass)
            else:
                self.append(Field(name=name, type=t))
                self._fields[name].label_text = field.title or name
                if field.description:
                    self._fields[name].set(instructions=field.description)
                if field.required:
                    self._fields[name].validators.append(validators.required)
                if klass is schema.Text:
                    self._fields[name].set(renderer=fields.TextAreaFieldRenderer)

    def bind(self, model, session=None, data=None):
        if not (model is not None or session or data):
            raise Exception('must specify at least one of {model, session, data}')
        # copy.copy causes a stacktrace on python 2.5.2/OSX + pylons.  unable to reproduce w/ simpler sample.
        mr = object.__new__(self.__class__)
        mr.__dict__ = dict(self.__dict__)
        # two steps so bind's error checking can work
        mr.rebind(model, session, data)
        mr._fields = OrderedDict([(key, renderer.bind(mr)) for key, renderer in self._fields.iteritems()])
        if self._render_fields:
            mr._render_fields = OrderedDict([(field.key, field) for field in
                                             [field.bind(mr) for field in self._render_fields.itervalues()]])
        return mr

    def gen_model(self, model=None):
        factory = gen_model(self.iface, model)
        model = factory(model)
        return model

    def rebind(self, model, session=None, data=None):
        if model is not self.iface:
            if model and not self.iface.providedBy(model):
                model = self.gen_model(model)
        self.model = model
        self._bound_pk = None
        if data is None:
            self.data = None
        elif hasattr(data, 'getall') and hasattr(data, 'getone'):
            self.data = data
        else:
            try:
                self.data = SimpleMultiDict(data)
            except:
                raise Exception('unsupported data object %s.  currently only dicts and Paste multidicts are supported' % self.data)

class Grid(BaseGrid, FieldSet):
    """Grid aware of zope schema. See :class:`formalchemy.tables.Grid` for full api."""
    def __init__(self, cls, instances=[], session=None, data=None, prefix=None):
        FieldSet.__init__(self, cls, session, data, prefix)
        self.rows = instances
        self.readonly = False
        self._errors = {}

    def _get_errors(self):
        return self._errors

    def _set_errors(self, value):
        self._errors = value
    errors = property(_get_errors, _set_errors)

    def rebind(self, instances=None, session=None, data=None):
        self.session = session
        self.data = data
        if instances is not None:
            self.rows = instances

    def _set_active(self, instance, session=None):
        FieldSet.rebind(self, instance, session or self.session, self.data)


