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
Date, Datetime, Time, and Choice.

Usage
=====

Here is a simple example. First we need a schema::

    >>> class IPet(interface.Interface):
    ...     name = schema.Text(title=u'Name', required=True)
    ...     type = schema.TextLine(title=u'Type', required=True)
    ...     age = schema.Int(min=1)
    ...     owner = schema.TextLine(title=u'Owner')
    ...     birthdate = schema.Date(title=u'Birth date')
    ...     colour = schema.Choice(title=u'Colour',
    ...                            values=['Brown', 'Black'])
    ...     friends = schema.List(title=u'Friends', value_type=schema.Choice(['cat', 'dog', 'bulldog']))

Initialize FieldSet with schema::

    >>> fs = FieldSet(IPet)

Create a class to store values. If your class does not implement the form interface the FieldSet will generate an adapter for you:

    >>> class Pet(FlexibleDict):pass
    >>> p = Pet(name='dewey', type='cat', owner='gawel', friends=['cat', 'dog'])
    >>> fs = fs.bind(p)

Fields are aware of schema attributes:

    >>> fs.name.is_required()
    True

We can use the form::

    >>> print fs.render().strip() #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    <div>
      <label class="field_req" for="Pet--name">Name</label>
      <textarea id="Pet--name" name="Pet--name">dewey</textarea>
    </div>
    <script type="text/javascript">
    //<![CDATA[
    document.getElementById("Pet--name").focus();
    //]]>
    </script>
    <div>
      <label class="field_req" for="Pet--type">Type</label>
      <input id="Pet--type" name="Pet--type" type="text" value="cat" />
    </div>
    <div>
      <label class="field_req" for="Pet--age">age</label>
      <input id="Pet--age" name="Pet--age" type="text" />
    </div>
    <div>
      <label class="field_req" for="Pet--owner">Owner</label>
      <input id="Pet--owner" name="Pet--owner" type="text" value="gawel" />
    </div>
    <div>
      <label class="field_req" for="Pet--birthdate">Birth date</label>
      <span id="Pet--birthdate"><select id="Pet--birthdate__month" name="Pet--birthdate__month">
    <option selected="selected" value="MM">Month</option>
    <option value="1">January</option>
    <option value="2">February</option>
    ...
    <option value="31">31</option>
    </select>
    <input id="Pet--birthdate__year" maxlength="4" name="Pet--birthdate__year" size="4" type="text" value="YYYY" /></span>
    </div>
    <div>
      <label class="field_req" for="Pet--colour">Colour</label>
      <select id="Pet--colour" name="Pet--colour">
    <option value="Brown">Brown</option>
    <option value="Black">Black</option>
    </select>
    </div>
    <div>
      <label class="field_req" for="Pet--friends">Friends</label>
      <select id="Pet--friends" multiple="multiple" name="Pet--friends">
    <option value="bulldog">bulldog</option>
    <option selected="selected" value="dog">dog</option>
    <option selected="selected" value="cat">cat</option>
    </select>
    </div>
    
Ok, let's assume that validation and syncing works:

    >>> fs.configure(include=[fs.name])
    >>> fs.rebind(p, data={'Pet--name':'minou'})
    >>> fs.validate()
    True
    >>> fs.sync()
    >>> fs.name.value
    u'minou'
    >>> p.name
    u'minou'

    >>> fs.configure(include=[fs.age])
    >>> fs.rebind(p, data={'Pet--age':'-1'})
    >>> fs.validate()
    False
    >>> fs.age.errors
    [u'Value is too small']
    >>> fs.configure(include=[fs.colour])
    >>> fs.rebind(p, data={'Pet--colour':'Yellow'})
    >>> fs.validate()
    False
    >>> fs.colour.errors
    [u'Constraint not satisfied']

    >>> fs.rebind(p, data={'Pet--colour':'Brown'})
    >>> fs.validate()
    True
    >>> fs.sync()
    >>> fs.colour.value
    u'Brown'
    >>> p.colour
    u'Brown'


Looks nice ! Let's use the grid:

    >>> grid = Grid(IPet)
    >>> grid = grid.bind([p])
    >>> print grid.render().strip() #doctest: +ELLIPSIS
    <thead>
      <tr>
          <th>Name</th>
          <th>Type</th>
          <th>age</th>
          <th>Owner</th>
          <th>Birth date</th>
          <th>Colour</th>
          <th>Friends</th>
      </tr>
    ...
      <tr class="even">
        <td>
          <textarea id="Pet--name" name="Pet--name">minou</textarea>
        </td>
        <td>
          <input id="Pet--type" name="Pet--type" type="text" value="cat" />
        </td>
        <td>
          <input id="Pet--age" name="Pet--age" type="text" />
        </td>
        <td>
          <input id="Pet--owner" name="Pet--owner" type="text" value="gawel" />
        </td>
        <td>
          <span id="Pet--birthdate"><select id="Pet--birthdate__month" name="Pet--birthdate__month">
    <option selected="selected" value="MM">Month</option>
    <option value="1">January</option>
    <option value="2">February</option>
    <option value="3">March</option>
    <option value="4">April</option>
    <option value="5">May</option>
    <option value="6">June</option>
    <option value="7">July</option>
    <option value="8">August</option>
    <option value="9">September</option>
    <option value="10">October</option>
    <option value="11">November</option>
    <option value="12">December</option>
    </select>
    <select id="Pet--birthdate__day" name="Pet--birthdate__day">
    <option selected="selected" value="DD">Day</option>
    <option value="1">1</option>
    ...
    <option value="31">31</option>
    </select>
    <input id="Pet--birthdate__year" maxlength="4" name="Pet--birthdate__year" size="4" type="text" value="YYYY" /></span>
        </td>
        <td>
          <select id="Pet--colour" name="Pet--colour">
    <option selected="selected" value="Brown">Brown</option>
    <option value="Black">Black</option>
    </select>
        </td>
        <td>
          <select id="Pet--friends" multiple="multiple" name="Pet--friends">
    <option value="bulldog">bulldog</option>
    <option selected="selected" value="dog">dog</option>
    <option selected="selected" value="cat">cat</option>
    </select>
        </td>
      </tr>
    </tbody>

"""
from formalchemy.forms import FieldSet as BaseFieldSet
from formalchemy.tables import Grid as BaseGrid
from formalchemy.fields import Field as BaseField
from formalchemy.forms import SimpleMultiDict
from formalchemy.fields import _stringify
from formalchemy import fields
from formalchemy import validators
from formalchemy import fatypes
from sqlalchemy.util import OrderedDict
from datetime import datetime
from uuid import UUID
from zope import schema
from zope.schema import interfaces
from zope import interface

class Pk(property):
    """FormAlchemy use a ``_pk`` attribute to identify objects. You can use
    this property to bind another attribute as a primary key::

        >>> class Content(object):
        ...     _pk = Pk()
        ...     __name__ = 'primary_key'

        >>> content = Content()
        >>> content._pk
        'primary_key'

        >>> content._pk = 'another_key'
        >>> content.__name__
        'another_key'

        >>> class Content(object):
        ...     _pk = Pk('uid')
        ...     uid = 'primary_key'

        >>> content = Content()
        >>> content._pk
        'primary_key'

        >>> fields._pk(content)
        'primary_key'
    """

    def __init__(self, attr='__name__'):
        self.attr = attr

    def __get__(self, instance, cls):
        return getattr(instance, self.attr, None) or None

    def __set__(self, instance, value):
        setattr(instance, self.attr, value)

class FlexibleModel(object):
    """A flexible object to easy adapt most python classes:

    .. sourcecode:: python

        >>> obj = FlexibleModel(owner='gawel')
        >>> obj.owner == obj.get('owner') == obj['owner'] == 'gawel'
        True
        >>> obj._pk is None
        True

    If your object provide an uuid attribute then FormAlchemy will use it has primary key:

    .. sourcecode:: python

        >>> import uuid
        >>> obj = FlexibleModel(uuid=uuid.uuid4())
        >>> obj._pk is None
        False

    """
    interface.implements(interface.Interface)
    _is_dict = False
    def __init__(self, context=None, **kwargs):
        if context is None:
            self.context = dict(**kwargs)
        else:
            self.context = context
        if getattr(self, 'uuid', None):
            uuid = self.uuid
            if isinstance(uuid, UUID):
                self._pk = str(int(uuid))
            else:
                self._pk = _stringify(self.uuid)
        else:
            self._pk = None

    def __getattr__(self, attr):
        """flexible __getattr__. also used for __getitem__ and get"""
        if hasattr(self.context, attr):
            return getattr(self.context, attr, None)
        elif self._is_dict or isinstance(self.context, dict):
            return self.context.get(attr)
        raise AttributeError('%r as no attribute %s' % (self.context, attr))
    __getitem__ = get = __getattr__

    def __setattr__(self, attr, value):
        """flexible __getattr__"""
        if attr.startswith('_') or attr == 'context':
            object.__setattr__(self, attr, value)
        elif not self._is_dict and hasattr(self.context, attr):
            setattr(self.context, attr, value)
        elif self._is_dict or isinstance(self.context, dict):
            self.context[attr] = value
        else:
            raise AttributeError('%r as no attribute %s' % (self.context, attr))
    def __repr__(self):
        return '<%s adapter for %s>' % (self.__class__.__name__, repr(self.context))

class FlexibleDict(FlexibleModel, dict):
    """like FlexibleModel but inherit from dict:

    .. sourcecode:: python

        >>> obj = FlexibleDict(owner='gawel')
        >>> obj.owner == obj.get('owner') == obj['owner'] == 'gawel'
        True
        >>> isinstance(obj, dict)
        True
        >>> 'owner' in obj
        True

    """
    interface.implements(interface.Interface)
    _is_dict = True
    def keys(self):
        return self.context.keys()
    def values(self):
        return self.context.values()
    def items(self):
        return self.context.items()
    def copy(self):
        return self.context.copy()
    def __iter__(self):
        return iter(self.context)
    def __contains__(self, value):
        return value in self.context

_model_registry = {}

def gen_model(iface, klass=None, dict_like=False):
    """return a new FlexibleModel or FlexibleDict factory who provide iface:

    .. sourcecode:: python

        >>> class ITitle(interfaces.Interface):
        ...     title = schema.TextLine(title=u'title')

        >>> factory = gen_model(ITitle)
        >>> adapted = factory()
        >>> ITitle.providedBy(adapted)
        True

        >>> class Title(object):
        ...     title = None
        >>> obj = Title()
        >>> adapted = factory(obj)
        >>> adapted.context is obj
        True
        >>> adapted.title = 'my title'
        >>> obj.title
        'my title'

        >>> obj = dict()
        >>> adapted = factory(obj)
        >>> adapted.context is obj
        True
        >>> adapted.title = 'my title'
        >>> obj['title']
        'my title'

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
    new_klass = type(name, (dict_like and FlexibleDict or FlexibleModel,), {})
    def adapter(context=None, **kwargs):
        adapted = new_klass(context=context, **kwargs)
        interface.directlyProvides(adapted, [iface])
        return adapted
    _model_registry[(iface.__name__, class_name)] = adapter
    return adapter

class Field(BaseField):
    """Field aware of zope schema. See :class:`formalchemy.fields.AbstractField` for full api."""

    def set(self, options=[], **kwargs):
        if isinstance(options, schema.Choice):
            sourcelist = options.source.by_value.values()
            if sourcelist[0].title is None:
                options = [term.value for term in sourcelist]
            else:
                options = [(term.title, term.value) for term in sourcelist]
        return BaseField.set(self, options=options, **kwargs)

    @property
    def value(self):
        if not self.is_readonly() and self.parent.data is not None:
            v = self._deserialize()
            if v is not None:
                return v
        return getattr(self.model, self.name)

    @property
    def raw_value(self):
        try:
            return getattr(self.model, self.name)
        except (KeyError, AttributeError):
            pass
        if callable(self._value):
            return self._value(self.model)
        return self._value

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
        except schema._bootstrapinterfaces.ConstraintNotSatisfied, e:
            self.errors.append(e.doc())

        return not self.errors

    def sync(self):
        """Set the attribute's value in `model` to the value given in `data`"""
        if not self.is_readonly():
            setattr(self.model, self.name, self._deserialize())


class FieldSet(BaseFieldSet):
    """FieldSet aware of zope schema. See :class:`formalchemy.forms.FieldSet` for full api."""

    __sa__ = False
    _fields_mapping = {
        schema.TextLine: fatypes.Unicode,
        schema.Text: fatypes.Unicode,
        schema.Int: fatypes.Integer,
        schema.Bool: fatypes.Boolean,
        schema.Float: fatypes.Float,
        schema.Date: fatypes.Date,
        schema.Datetime: fatypes.DateTime,
        schema.Time: fatypes.Time,
        schema.Choice: fatypes.Unicode,
        schema.List: fatypes.List,
        schema.Password: fatypes.Unicode,
    }

    def __init__(self, model, **kwargs):
        BaseFieldSet.__init__(self, model, **kwargs)
        self.iface = model
        self.rebind(model)
        self._fields = OrderedDict()
        self._render_fields = OrderedDict()
        self._bound_pk = None
        for name, field in schema.getFieldsInOrder(self.iface):
            klass = field.__class__
            try:
                t = self._fields_mapping[klass]
            except KeyError:
                raise NotImplementedError('%s is not mapped to a type' % klass)
            else:
                self.append(Field(name=name, type=t))
                self._fields[name].label_text = field.title or name
                if field.description:
                    self._fields[name].set(instructions=field.description)
                if field.required:
                    self._fields[name].validators.append(validators.required)
                if klass is schema.Password:
                    self._fields[name].set(renderer=fields.PasswordFieldRenderer)
                if klass is schema.Text:
                    self._fields[name].set(renderer=fields.TextAreaFieldRenderer)
                if klass is schema.List:
                    value_type = self.iface[name].value_type
                    if isinstance(value_type, schema.Choice):
                        self._fields[name].set(options=value_type, multiple=True)
                    else:
                        self._fields[name].set(multiple=True)
                elif klass is schema.Choice:
                    self._fields[name].set(renderer=fields.SelectFieldRenderer,
                                           options=self.iface[name])

    def bind(self, model, session=None, data=None, request=None):
        if not (model is not None or session or data):
            raise Exception('must specify at least one of {model, session, data}')
        # copy.copy causes a stacktrace on python 2.5.2/OSX + pylons.  unable to reproduce w/ simpler sample.
        mr = object.__new__(self.__class__)
        mr.__dict__ = dict(self.__dict__)
        # two steps so bind's error checking can work
        mr.rebind(model, session, data)
        mr._request = request
        mr._fields = OrderedDict([(key, renderer.bind(mr)) for key, renderer in self._fields.iteritems()])
        if self._render_fields:
            mr._render_fields = OrderedDict([(field.key, field) for field in
                                             [field.bind(mr) for field in self._render_fields.itervalues()]])
        return mr

    def gen_model(self, model=None, dict_like=False, **kwargs):
        if model and self.iface.providedBy(model):
            return model
        factory = gen_model(self.iface, model, dict_like=dict_like)
        model = factory(context=model, **kwargs)
        return model

    def rebind(self, model, session=None, data=None):
        if model is not self.iface:
            if model and not self.iface.providedBy(model):
                if getattr(model, '__implemented__', None) is not None:
                    raise ValueError('%r does not provide %r' % (model, self.iface))
                model = self.gen_model(model)
        self.model = model
        self._bound_pk = fields._pk(model)
        if data is None:
            self.data = None
        elif hasattr(data, 'getall') and hasattr(data, 'getone'):
            self.data = data
        else:
            try:
                self.data = SimpleMultiDict(data)
            except:
                raise Exception('unsupported data object %s. currently only dicts and Paste multidicts are supported' % self.data)

class Grid(BaseGrid, FieldSet):
    """Grid aware of zope schema. See :class:`formalchemy.tables.Grid` for full api."""
    __sa__ = False
    def __init__(self, cls, instances=[], **kwargs):
        FieldSet.__init__(self, cls, **kwargs)
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

    def bind(self, instances=None, session=None, data=None):
        mr = FieldSet.bind(self, self.iface, session, data)
        mr.rows = instances
        return mr

    def _set_active(self, instance, session=None):
        instance = self.gen_model(instance)
        FieldSet.rebind(self, instance, session or self.session, self.data)


