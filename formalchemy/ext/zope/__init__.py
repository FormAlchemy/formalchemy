# -*- coding: utf-8 -*-
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
            import pdb;pdb.set_trace()
            self.errors.append(e.doc())

        return not self.errors

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
                if field.title:
                    self._fields[name].label_text = field.title
                if field.required:
                    self._fields[name].validators.append(validators.required)
                if klass is schema.Text:
                    self._fields[name].set(renderer=fields.TextAreaFieldRenderer)

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
        self.session = session
        self.data = data
        if instances is not None:
            self.rows = instances

    def _set_active(self, instance, session=None):
        FieldSet.rebind(self, instance, session or self.session, self.data)

def test_fieldset():

    class IPet(interface.Interface):
        name = schema.Text(
            title=u'Name',
            required=True)
        type = schema.TextLine(
            title=u'Type',
            required=True)
        age = schema.Int(min=1)
        owner = schema.TextLine(
            title=u'Owner')
        birthdate = schema.Date(title=u'Birth date')

    class Pet(object):
        interface.implements(IPet)
        def __init__(self):
            self.name = ''
            self.type = ''
            self.age = ''
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
    assert 'Birth date' in html, html

    # syncing
    fs.configure(include=[fs.name])
    fs.rebind(p, data={'Pet--name':'minou'})
    fs.validate()
    fs.sync()
    assert fs.name.value == 'minou', fs.render_fields
    assert p.name == 'minou', p.name

    fs.configure(include=[fs.age])
    fs.rebind(p, data={'Pet--age':'-1'})
    fs.validate()
    assert fs.age.errors == [u'Value is too small'], fs.errors

