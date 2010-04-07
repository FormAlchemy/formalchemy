# -*- coding: utf-8 -*-
__doc__ = """This module provides an experimental subclass of
:class:`~formalchemy.forms.FieldSet` to support RDFAlchemy_.

.. _RDFAlchemy: http://www.openvest.com/trac/wiki/RDFAlchemy

Usage
=====

    >>> from rdfalchemy.samples.company import Company
    >>> c = Company(stockDescription='description', symbol='FA',
    ...             cik='cik', companyName='fa corp',
    ...             stock=['value1'])

    >>> fs = FieldSet(Company)
    >>> fs.configure(options=[fs.stock.set(options=['value1', 'value2'])])
    >>> fs = fs.bind(c)
    >>> fs.stock.value
    ['value1']

    >>> print fs.render().strip() # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    <div>
      <label class="field_opt" for="Company--stockDescription">Stockdescription</label>
      <input id="Company--stockDescription" name="Company--stockDescription" type="text" value="description" />
    </div>
    ...
    <div>
      <label class="field_opt" for="Company--stock">Stock</label>
      <select id="Company--stock" name="Company--stock">
    <option selected="selected" value="value1">value1</option>
    <option value="value2">value2</option>
    </select>
    </div>
    

    >>> fs = Grid(Company, [c])
    >>> fs.configure(options=[fs.stock.set(options=['value1', 'value2'])], readonly=True)
    >>> print fs.render().strip() #doctest: +NORMALIZE_WHITESPACE
    <thead>
      <tr>
          <th>Stockdescription</th>
          <th>Companyname</th>
          <th>Cik</th>
          <th>Symbol</th>
          <th>Stock</th>
      </tr>
    </thead>
    <tbody>
      <tr class="even">
        <td>description</td>
        <td>fa corp</td>
        <td>cik</td>
        <td>FA</td>
        <td>value1</td>
      </tr>
    </tbody>
    

"""
from formalchemy.forms import FieldSet as BaseFieldSet
from formalchemy.tables import Grid as BaseGrid
from formalchemy.fields import Field as BaseField
from formalchemy.base import SimpleMultiDict
from formalchemy import fields
from formalchemy import validators
from formalchemy import fatypes
from sqlalchemy.util import OrderedDict
from rdfalchemy import descriptors

from datetime import datetime


__all__ = ['Field', 'FieldSet']

class Session(object):
    """A SA like Session to implement rdf"""
    def add(self, record):
        """add a record"""
        record.save()
    def update(self, record):
        """update a record"""
        record.save()
    def delete(self, record):
        """delete a record"""
    def query(self, model, *args, **kwargs):
        raise NotImplementedError()
    def commit(self):
        """do nothing since there is no transaction in couchdb"""
    remove = commit

class Field(BaseField):
    """"""

    @property
    def value(self):
        if not self.is_readonly() and self.parent.data is not None:
            v = self._deserialize()
            if v is not None:
                return v
        return getattr(self.model, self.name)

    @property
    def model_value(self):
        return getattr(self.model, self.name)
    raw_value = model_value

    def sync(self):
        """Set the attribute's value in `model` to the value given in `data`"""
        if not self.is_readonly():
            setattr(self.model, self.name, self._deserialize())

class FieldSet(BaseFieldSet):
    _mapping = {
            descriptors.rdfSingle: fatypes.String,
            descriptors.rdfMultiple: fatypes.List,
            descriptors.rdfList: fatypes.List,
        }

    def __init__(self, model, session=None, data=None, prefix=None):
        self._fields = OrderedDict()
        self._render_fields = OrderedDict()
        self.model = self.session = None
        BaseFieldSet.rebind(self, model, data=data)
        self.prefix = prefix
        self.model = model
        self.readonly = False
        self.focus = True
        self._errors = []
        focus = True
        for k, v in model.__dict__.iteritems():
            if not k.startswith('_'):
                descriptor = type(v)
                t = self._mapping.get(descriptor)
                if t:
                    self.append(Field(name=k, type=t))

    def bind(self, model=None, session=None, data=None):
        """Bind to an instance"""
        if not (model or session or data):
            raise Exception('must specify at least one of {model, session, data}')
        if not model:
            if not self.model:
                raise Exception('model must be specified when none is already set')
            else:
                model = self.model()
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

    def rebind(self, model, session=None, data=None):
        if model:
            if isinstance(model, type):
                try:
                    model = model()
                except:
                    raise Exception('%s appears to be a class, not an instance, but FormAlchemy cannot instantiate it.  (Make sure all constructor parameters are optional!)' % model)
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
        FieldSet.rebind(data=data)
        if instances is not None:
            self.rows = instances

    def _set_active(self, instance, session=None):
        FieldSet.rebind(self, instance, session or self.session, self.data)

def test_sync():
    from rdfalchemy.samples.company import Company
    c = Company(stockDescription='description', symbol='FA',
                cik='cik', companyName='fa corp',
                stock=['value1'])

    fs = FieldSet(Company)
    fs.configure(include=[fs.companyName, fs.stock.set(options=['value1', 'value2'])])
    fs = fs.bind(c, data={'Company--companyName':'new name', 'Company--stock':'value2'})
    assert fs.stock.raw_value == ['value1']

    fs.validate()
    fs.sync()

    assert fs.stock.raw_value == ['value2']

