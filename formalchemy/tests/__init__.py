# -*- coding: utf-8 -*-
import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

from BeautifulSoup import BeautifulSoup # required for html prettification

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)

from formalchemy.fields import Field, SelectFieldRenderer, FieldRenderer, TextFieldRenderer
import formalchemy.fatypes as types

engine = create_engine('sqlite://')
Session = scoped_session(sessionmaker(autoflush=False, bind=engine))
Base = declarative_base(engine, mapper=Session.mapper)

class One(Base):
    __tablename__ = 'ones'
    id = Column('id', Integer, primary_key=True)

class Two(Base):
    __tablename__ = 'twos'
    id = Column('id', Integer, primary_key=True)
    foo = Column('foo', Integer, default='133', nullable=True)

class Three(Base):
    __tablename__ = 'threes'
    id = Column('id', Integer, primary_key=True)
    foo = Column('foo', Text, nullable=True)
    bar = Column('bar', Text, nullable=True)

class CheckBox(Base):
    __tablename__ = 'checkboxes'
    id = Column('id', Integer, primary_key=True)
    field = Column('field', Boolean, nullable=False)

class Binaries(Base):
    __tablename__ = 'binaries'
    id = Column('id', Integer, primary_key=True)
    file = Column('file', Binary, nullable=True)

vertices = Table('vertices', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('x1', Integer),
    Column('y1', Integer),
    Column('x2', Integer),
    Column('y2', Integer),
    )

class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __composite_values__(self):
        return [self.x, self.y]
    def __eq__(self, other):
        return other.x == self.x and other.y == self.y
    def __ne__(self, other):
        return not self.__eq__(other)

class Vertex(object):
    pass

Session.mapper(Vertex, vertices, properties={
    'start':composite(Point, vertices.c.x1, vertices.c.y1),
    'end':composite(Point, vertices.c.x2, vertices.c.y2)
})

class VertexFieldRenderer(FieldRenderer):
    def render(self, **kwargs):
        import helpers as h
        data = self.field.parent.data
        x_name = self.name + '-x'
        y_name = self.name + '-y'
        x_value = (data is not None and x_name in data) and data[x_name] or str(self._value and self._value.x or '')
        y_value = (data is not None and y_name in data) and data[y_name] or str(self._value and self._value.y or '')
        return h.text_field(x_name, value=x_value) + h.text_field(y_name, value=y_value)
    def deserialize(self):
        data = self.field.parent.data.getone(self.name + '-x'), self.field.parent.data.getone(self.name + '-y')
        return Point(*[int(i) for i in data])


# todo? test a CustomBoolean, using a TypeDecorator --
# http://www.sqlalchemy.org/docs/04/types.html#types_custom
# probably need to add _renderer attr and check
# isinstance(getattr(myclass, '_renderer', type(myclass)), Boolean)
# since the custom class shouldn't really inherit from Boolean

class OTOChild(Base):
    __tablename__ = 'one_to_one_child'
    id = Column('id', Integer, primary_key=True)
    baz = Column('foo', Text, nullable=False)

class OTOParent(Base):
    __tablename__ = 'one_to_one_parent'
    id = Column('id', Integer, primary_key=True)
    oto_child_id = Column('oto_child_id', Integer, ForeignKey('one_to_one_child.id'), nullable=False)
    child = relation(OTOChild, uselist=False)

class Order(Base):
    __tablename__ = 'orders'
    id = Column('id', Integer, primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('users.id'), nullable=False)
    quantity = Column('quantity', Integer, nullable=False)
    def __str__(self):
        return 'Quantity: %s' % self.quantity

class User(Base):
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key=True)
    email = Column('email', Unicode(40), unique=True, nullable=False)
    password = Column('password', Unicode(20), nullable=False)
    name = Column('name', Unicode(30))
    orders = relation(Order, backref='user')
    def __str__(self):
        return self.name

class NaturalOrder(Base):
    __tablename__ = 'natural_orders'
    id = Column('id', Integer, primary_key=True)
    user_email = Column('user_email', String, ForeignKey('natural_users.email'), nullable=False)
    quantity = Column('quantity', Integer, nullable=False)
    def __str__(self):
        return 'Quantity: %s' % self.quantity

class NaturalUser(Base):
    __tablename__ = 'natural_users'
    email = Column('email', Unicode(40), primary_key=True)
    password = Column('password', Unicode(20), nullable=False)
    name = Column('name', Unicode(30))
    orders = relation(NaturalOrder, backref='user')
    def __str__(self):
        return self.name

# test property order for non-declarative mapper
addresses = Table('email_addresses', Base.metadata,
    Column('address_id', Integer, Sequence('address_id_seq', optional=True), primary_key = True),
    Column('address', String(40)),
)
users2 = Table('users2', Base.metadata,
    Column('user_id', Integer, Sequence('user_id_seq', optional=True), primary_key = True),
    Column('address_id', Integer, ForeignKey(addresses.c.address_id)),
    Column('name', String(40), nullable=False)
)
class Address(object): pass
class User2(object): pass
mapper(Address, addresses)
mapper(User2, users2, properties={'address': relation(Address)})


class Manual(object):
    a = Field()
    b = Field(type=types.Integer).dropdown([('one', 1), ('two', 2)], multiple=True)


class Order__User(Base):
    __table__ = join(Order.__table__, User.__table__).alias('__orders__users')

class Aliases(Base):
    __tablename__ = 'table_with_aliases'
    id = Column('row_id', Integer, primary_key=True)
    text = Column('row_text', Text)

Base.metadata.create_all()

session = Session()

bill = User(email='bill@example.com',
            password='1234',
            name='Bill')
john = User(email='john@example.com',
            password='5678',
            name='John')
order1 = Order(user=bill, quantity=10)
order2 = Order(user=john, quantity=5)
order3 = Order(user=john, quantity=6)

nbill = NaturalUser(email='nbill@example.com',
                    password='1234',
                    name='Natural Bill')
njohn = NaturalUser(email='njohn@example.com',
                    password='5678',
                    name='Natural John')
norder1 = NaturalOrder(user=nbill, quantity=10)
norder2 = NaturalOrder(user=njohn, quantity=5)

session.commit()


from formalchemy.forms import FieldSet as DefaultFieldSet, render_tempita, render_readonly
try:
    import mako
except ImportError:
    pass
from formalchemy.fields import Field, query_options
from formalchemy.validators import ValidationError

def pretty_html(html):
    soup = BeautifulSoup(html)
    return soup.prettify().strip()

class FieldSet(DefaultFieldSet):
    def render(self, lang=None):
        if self.readonly:
            return pretty_html(DefaultFieldSet.render(self))
        html = pretty_html(DefaultFieldSet.render(self))
        if 'mako' in globals():
            # FS will use mako by default, so test tempita for equivalence here
            F_ = lambda s: s
            html_tempita = pretty_html(render_tempita(fieldset=self, F_=F_))
            assert html == html_tempita
        return html

original_renderers = FieldSet.default_renderers.copy()

def configure_and_render(fs, **options):
    fs.configure(**options)
    return fs.render()

if not hasattr(__builtins__, 'sorted'):
    # 2.3 support
    def sorted(L, key=None):
        assert key
        L = list(L)
        L.sort(lambda a, b: cmp(key(a), key(b)))
        return L

class ImgRenderer(TextFieldRenderer):
    def render(self, *args, **kwargs):
        return '<img src="%s">' % self._value

import fake_module
fake_module.__dict__.update({
        'fs': FieldSet(User),
        })
import sys
sys.modules['library'] = fake_module
