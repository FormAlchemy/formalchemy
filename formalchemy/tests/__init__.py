# -*- coding: utf-8 -*-
import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

from BeautifulSoup import BeautifulSoup # required for html prettification

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)

from formalchemy.fields import Field, SelectFieldRenderer, FieldRenderer, TextFieldRenderer, EscapingReadonlyRenderer
import formalchemy.fatypes as types

engine = create_engine('sqlite://')
Session = scoped_session(sessionmaker(autoflush=False, bind=engine))
Base = declarative_base(engine, mapper=Session.mapper)

class One(Base):
    __tablename__ = 'ones'
    id = Column(Integer, primary_key=True)

class Two(Base):
    __tablename__ = 'twos'
    id = Column(Integer, primary_key=True)
    foo = Column(Integer, default='133', nullable=True)

class TwoFloat(Base):
    __tablename__ = 'two_floats'
    id = Column(Integer, primary_key=True)
    foo = Column(Float, nullable=False)

from decimal import Decimal
class TwoNumeric(Base):
    __tablename__ = 'two_numerics'
    id = Column(Integer, primary_key=True)
    foo = Column(Numeric, nullable=True)

class Three(Base):
    __tablename__ = 'threes'
    id = Column(Integer, primary_key=True)
    foo = Column(Text, nullable=True)
    bar = Column(Text, nullable=True)

class CheckBox(Base):
    __tablename__ = 'checkboxes'
    id = Column(Integer, primary_key=True)
    field = Column(Boolean, nullable=False)

class PrimaryKeys(Base):
    __tablename__ = 'primary_keys'
    id = Column(Integer, primary_key=True)
    id2 = Column(String(10), primary_key=True)
    field = Column(String(10), nullable=False)

class Binaries(Base):
    __tablename__ = 'binaries'
    id = Column(Integer, primary_key=True)
    file = Column(Binary, nullable=True)


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

class Recursive(Base):
    __tablename__ = 'recursives'
    id = Column(Integer, primary_key=True)
    foo = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("recursives.id"))
    parent = relation('Recursive', primaryjoin=parent_id==id, uselist=False, remote_side=parent_id)

class OTOChild(Base):
    __tablename__ = 'one_to_one_child'
    id = Column(Integer, primary_key=True)
    baz = Column(Text, nullable=False)

class OTOParent(Base):
    __tablename__ = 'one_to_one_parent'
    id = Column(Integer, primary_key=True)
    oto_child_id = Column(Integer, ForeignKey('one_to_one_child.id'), nullable=False)
    child = relation(OTOChild, uselist=False)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    def __str__(self):
        return 'Quantity: %s' % self.quantity

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(Unicode(40), unique=True, nullable=False)
    password = Column(Unicode(20), nullable=False)
    name = Column(Unicode(30))
    orders = relation(Order, backref='user')
    def __str__(self):
        return self.name

class NaturalOrder(Base):
    __tablename__ = 'natural_orders'
    id = Column(Integer, primary_key=True)
    user_email = Column(String, ForeignKey('natural_users.email'), nullable=False)
    quantity = Column(Integer, nullable=False)
    def __str__(self):
        return 'Quantity: %s' % self.quantity

class NaturalUser(Base):
    __tablename__ = 'natural_users'
    email = Column(Unicode(40), primary_key=True)
    password = Column(Unicode(20), nullable=False)
    name = Column(Unicode(30))
    orders = relation(NaturalOrder, backref='user')
    def __str__(self):
        return self.name

class Function(Base):
    __tablename__ = 'functions'
    foo = Column(TIMESTAMP, primary_key=True, default=func.current_timestamp())

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
    d = Field().textarea((80, 10))


class OrderUser(Base):
    __tablename__ = 'order_users'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), primary_key=True)
    user = relation(User)
    order = relation(Order)
    def __str__(self):
        return 'OrderUser(%s, %s)' % (self.user_id, self.order_id)
    
class OrderUserTag(Base):
    __table__ = Table('order_user_tags', Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('user_id', Integer, nullable=False),
                      Column('order_id', Integer, nullable=False),
                      Column('tag', String, nullable=False),
                      ForeignKeyConstraint(['user_id', 'order_id'], ['order_users.user_id', 'order_users.order_id']))
    order_user = relation(OrderUser)


class Order__User(Base):
    __table__ = join(Order.__table__, User.__table__).alias('__orders__users')

class Aliases(Base):
    __tablename__ = 'table_with_aliases'
    id = Column(Integer, primary_key=True)
    text = Column('row_text', Text)

Base.metadata.create_all()

session = Session()

primary1 = PrimaryKeys(id=1, id2='22', field='value1')
primary2 = PrimaryKeys(id=1, id2='33', field='value2')

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

orderuser1 = OrderUser(user_id=1, order_id=1)
orderuser2 = OrderUser(user_id=1, order_id=2)

session.commit()


from formalchemy.forms import FieldSet as DefaultFieldSet, render_tempita, render_readonly
try:
    import mako
except ImportError:
    pass
from formalchemy.fields import Field
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
    def sorted(L, key=lambda a: a):
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
