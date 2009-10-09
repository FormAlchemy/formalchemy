# -*- coding: utf-8 -*-
__doc__ = """

Define a couchdbkit schema::

    >>> from couchdbkit import schema
    >>> from formalchemy.ext import couchdb
    >>> class Pet(couchdb.Document):
    ...     name = schema.StringProperty(required=True)
    ...     type = schema.StringProperty(required=True)
    ...     birthdate = schema.DateProperty(auto_now=True)
    ...     weight_in_pounds = schema.IntegerProperty()
    ...     spayed_or_neutered = schema.BooleanProperty()
    ...     owner = schema.StringProperty()

Configure your FieldSet::

    >>> fs = couchdb.FieldSet(Pet)
    >>> fs.configure(include=[fs.name, fs.type, fs.birthdate, fs.weight_in_pounds])
    >>> p = Pet(name='dewey')
    >>> p.name = 'dewey'
    >>> p.type = 'cat'
    >>> fs = fs.bind(p)

Render it::

    >>> # rendering
    >>> fs.name.is_required()
    True
    >>> print fs.render() # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    <div>
      <label class="field_req" for="Pet--name">Name</label>
      <input id="Pet--name" name="Pet--name" type="text" value="dewey" />
    </div>
    <BLANKLINE>
    <script type="text/javascript">
    //<![CDATA[
    document.getElementById("Pet--name").focus();
    //]]>
    </script>
    <div>
      <label class="field_req" for="Pet--type">Type</label>
      <input id="Pet--type" name="Pet--type" type="text" value="cat" />
    </div>
    <BLANKLINE>
    <div>
      <label class="field_opt" for="Pet--birthdate">Birthdate</label>
      <span id="Pet--birthdate"><select id="Pet--birthdate__month" name="Pet--birthdate__month"><option value="MM">Month</option>
    <option value="1">January</option>
    ...
    
Same for grids::

    >>> # grid
    >>> grid = couchdb.Grid(Pet, [p, Pet()])
    >>> grid.configure(include=[grid.name, grid.type, grid.birthdate, grid.weight_in_pounds])
    >>> print grid.render() # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    <thead>
      <tr>
          <th>Name</th>
          <th>Type</th>
          <th>Birthdate</th>
          <th>Weight in pounds</th>
      </tr>
    </thead>
    <tbody>
      <tr class="even">
        <td>
          <input id="Pet--name" name="Pet--name" type="text" value="dewey" />
        </td>
        <td>
          <input id="Pet--type" name="Pet--type" type="text" value="cat" />
        </td>
        <td>
          <span id="Pet--birthdate">...

"""
from formalchemy.forms import FieldSet as BaseFieldSet
from formalchemy.tables import Grid as BaseGrid
from formalchemy.fields import Field as BaseField
from formalchemy.base import SimpleMultiDict
from formalchemy import fields
from formalchemy import validators
from formalchemy import fatypes
from sqlalchemy.util import OrderedDict
from couchdbkit import schema

from datetime import datetime


__all__ = ['Field', 'FieldSet', 'Session', 'Document']

class Pk(property):
    def __init__(self, attr='_id'):
        self.attr = attr
    def __get__(self, instance, cls):
        return getattr(instance, self.attr, None) or None
    def __set__(self, instance, value):
        setattr(instance, self.attr, value)

class Document(schema.Document):
    _pk = Pk()

class Query(list):
    """A list like object to emulate SQLAlchemy's Query. This mostly exist to
    work with ``webhelpers.paginate.Page``"""

    def __init__(self, model, **option):
        self.model = model
        self._init = False
        self.options = kwargs
    def get(self, id):
        """Get a record by id"""
        return self.model.get(id)
    def view(self, view_name, **kwargs):
        """set self to a list of record returned by view named ``{model_name}/{view_name}``"""
        kwargs = kwargs or self.options
        if not self._init:
            self.extend([r for r in self.model.view('%s/%s' % (self.model.__name__.lower(), view_name), **kwargs)])
            self._init = True
        return self
    def all(self, **kwargs):
        """set self to a list of record returned by view named ``{model_name}/all``"""
        kwargs = kwargs or self.options
        return self.view('all', **kwargs)
    def __len__(self):
        if not self._init:
            self.all()
        return list.__len__(self)

class Session(object):
    """A SA like Session to implement couchdb"""
    def __init__(self, db):
        self.db = db
    def add(self, record):
        """add a record"""
        record.save()
    def update(self, record):
        """update a record"""
        record.save()
    def delete(self, record):
        """delete a record"""
        del self.db[record._id]
    def query(self, model, *args, **kwargs):
        """return a :class:`~formalchemy.ext.couchdb.Query` bound to model object"""
        return Query(model, *args, **kwargs)
    def commit(self):
        """do nothing since there is no transaction in couchdb"""

class Field(BaseField):
    """"""
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

    def sync(self):
        """Set the attribute's value in `model` to the value given in `data`"""
        if not self.is_readonly():
            setattr(self.model, self.name, self._deserialize())

class FieldSet(BaseFieldSet):
    """See :class:`~formalchemy.forms.FieldSet`"""
    def __init__(self, model, session=None, data=None, prefix=None):
        self._fields = OrderedDict()
        self._render_fields = OrderedDict()
        self.model = self.session = None
        if model is not None and isinstance(model, schema.Document):
            BaseFieldSet.rebind(self, model.__class__, data=data)
            self.doc = model.__class__
            self._bound_pk = fields._pk(model)
        else:
            BaseFieldSet.rebind(self, model, data=data)
            self.doc = model
        self.model = model
        self.prefix = prefix
        self.validator = None
        self.readonly = False
        self.focus = True
        self._errors = []
        focus = True
        for k, v in self.doc().iteritems():
            if not k.startswith('_'):
                try:
                    t = getattr(fatypes, v.__class__.__name__.replace('Property',''))
                except AttributeError:
                    raise NotImplementedError('%s is not mapped to a type' % v.__class__)
                else:
                    self.append(Field(name=k, type=t))
                    if v.required:
                        self._fields[k].validators.append(validators.required)

    def bind(self, model=None, session=None, data=None):
        """Bind to an instance"""
        if not (model or session or data):
            raise Exception('must specify at least one of {model, session, data}')
        if not model:
            if not self.model:
                raise Exception('model must be specified when none is already set')
            model = fields._pk(self.model) is None and self.doc() or self.model
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

    def rebind(self, model=None, session=None, data=None):
        if model is not None and model is not self.doc:
            if not isinstance(model, self.doc):
                try:
                    model = model()
                except Exception, e:
                    raise Exception('''%s appears to be a class, not an instance,
                            but FormAlchemy cannot instantiate it.  (Make sure
                            all constructor parameters are optional!) %r - %s''' % (
                            model, self.doc, e))
        else:
            model = self.doc()
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
                raise Exception('unsupported data object %s.  currently only dicts and Paste multidicts are supported' % self.data)

    def jsonify(self):
        if isinstance(self.model, schema.Document):
            return self.model.to_json()
        return self.doc().to_json()

class Grid(BaseGrid, FieldSet):
    """See :class:`~formalchemy.tables.Grid`"""
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
        FieldSet.rebind(self, self.model, data=data)
        if instances is not None:
            self.rows = instances

    def bind(self, instances=None, session=None, data=None):
        mr = FieldSet.bind(self, self.model, session, data)
        mr.rows = instances
        return mr

    def _set_active(self, instance, session=None):
        FieldSet.rebind(self, instance, session or self.session, self.data)

