# -*- coding: utf-8 -*-
from formalchemy.forms import FieldSet as BaseFieldSet
from formalchemy.tables import Grid as BaseGrid
from formalchemy.fields import Field as BaseField
from formalchemy.base import SimpleMultiDict
from formalchemy import fields
from formalchemy import validators
from sqlalchemy.util import OrderedDict
import fatypes
from datetime import datetime
from zope import schema
from zope import interface

FIELDS_MAPPING = {
        schema.TextLine: fatypes.String,
        schema.Int: fatypes.Integer,
        schema.Date: fatypes.Date,
        schema.Datetime: fatypes.DateTime,
    }

class Field(BaseField):
    """"""
    def value(self):
        if not self.is_readonly() and self.parent.data is not None:
            v = self._deserialize()
            if v is not None:
                return v
        return getattr(self.model, self.name)
    value = property(value)

    def sync(self):
        """Set the attribute's value in `model` to the value given in `data`"""
        if not self.is_readonly():
            setattr(self.model, self.name, self._deserialize())


class FieldSet(BaseFieldSet):
    def __init__(self, model, session=None, data=None, prefix=None):
        self._fields = OrderedDict()
        self._render_fields = OrderedDict()
        self.model = self.session = None
        self.prefix = prefix
        self.model = model
        self.readonly = False
        self.focus = True
        self._errors = []
        self.iface = model
        focus = True
        for name, field in schema.getFields(model).items():
            try:
                t = FIELDS_MAPPING[field.__class__]
            except AttributeError:
                raise NotImplementedError('%s is not mapped to a type' % field.__class__)
            else:
                self.add(Field(name=name, type=t))
                if field.required:
                    self._fields[name].validators.append(validators.required)

    def bind(self, model, session=None, data=None):
        """Bind to an instance"""
        if not (model or session or data):
            raise Exception('must specify at least one of {model, session, data}')
        if not model:
            if not self.model:
                raise Exception('model must be specified when none is already set')
            model = fields._pk(self.model) is None and type(self.model) or self.model
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
            if not self.iface.providedBy(model):
                raise Exception('%r is not provided by %r' % (self.iface, model))
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

def test_fieldset():

    class IPet(interface.Interface):
        name = schema.TextLine(
            title=u'Name',
            required=True)
        type = schema.TextLine(
            title=u'Type',
            required=True)
        owner = schema.TextLine(
            title=u'Owner')
        birthdate = schema.Datetime(title=u'Birth date')

    class Pet(object):
        interface.implements(IPet)
        def __init__(self):
            self.name = ''
            self.type = ''
            self.owner = ''
            self.birthdate = ''

    fs = FieldSet(IPet)
    p = Pet()
    p.name = 'dewey'
    p.type = 'cat'
    p.owner = 'gawel'
    fs = fs.bind(p)

    # rendering
    assert fs.name.is_required() == True, fs.name.is_required()
    assert fs.owner.value == 'gawel', fs.owner.value
    html = fs.render()
    assert 'class="field_req" for="Pet--name"' in html, html
    assert 'value="gawel"' in html, html

    # syncing
    fs.configure(include=[fs.name])
    fs.rebind(p, data={'Pet--name':'minou'})
    fs.validate()
    fs.sync()
    assert fs.name.value == 'minou', fs.render_fields
    assert p.name == 'minou', p.name


