import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

from BeautifulSoup import BeautifulSoup # required for html prettification

from sqlalchemy import *
from sqlalchemy.orm import *
import sqlalchemy.types as types
from sqlalchemy.ext.declarative import declarative_base
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)

engine = create_engine('sqlite://')
Session = scoped_session(sessionmaker(autoflush=True, bind=engine))
Base = declarative_base(engine, mapper=Session.mapper)

class One(Base):
    __tablename__ = 'ones'
    id = Column('id', Integer, primary_key=True)

class Two(Base):
    __tablename__ = 'twos'
    id = Column('id', Integer, primary_key=True)
    foo = Column('foo', Text, nullable=True)

class Three(Base):
    __tablename__ = 'threes'
    id = Column('id', Integer, primary_key=True)
    foo = Column('foo', Text, nullable=True)
    bar = Column('bar', Text, nullable=True)

class Checkbox(Base):
    __tablename__ = 'checkboxes'
    id = Column('id', Integer, primary_key=True)
    field = Column('field', Boolean, nullable=False)
    
# todo: test a CustomBoolean, using a TypeDecorator --
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

nbill = NaturalUser(email='nbill@example.com', 
                    password='1234',
                    name='Natural Bill')
njohn = NaturalUser(email='njohn@example.com', 
                    password='5678',
                    name='Natural John')
norder1 = NaturalOrder(user=nbill, quantity=10)
norder2 = NaturalOrder(user=njohn, quantity=5)

session.commit()


from forms import FieldSet as DefaultFieldSet, render_mako, render_tempita
from fields import Field, query_options
from validators import ValidationException
from tables import Table, TableCollection

def _pretty_html(html):
    soup = BeautifulSoup(html)
    return soup.prettify().strip()

class FieldSet(DefaultFieldSet):
    def render(self):
        import fields
        kwargs = dict(attrs=self.render_attrs, global_errors=self._errors, fields=fields, prettify=self.prettify, focus=self.focus)
        tempita = _pretty_html(render_tempita(**kwargs))
        mako = _pretty_html(render_mako(**kwargs))
        assert mako == tempita
        return mako

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

__doc__ = r"""
# some low-level testing first
>>> fs = FieldSet(order1)
>>> list(sorted(fs._raw_attrs(), key=lambda attr: attr.key))
[AttributeField(id), AttributeField(quantity), AttributeField(user), AttributeField(user_id)]

>>> fs = FieldSet(bill)
>>> list(sorted(fs._raw_attrs(), key=lambda attr: attr.key))
[AttributeField(email), AttributeField(id), AttributeField(name), AttributeField(orders), AttributeField(password)]

>>> fs = FieldSet(One)
>>> fs.configure(pk=True, focus=None)
>>> fs.id.is_required()
True
>>> print fs.render()
<div>
 <label class="field_req" for="id">
  Id
 </label>
 <input id="id" name="id" type="text" />
</div>

>>> fs = FieldSet(Two)
>>> fs.configure(pk=True)
>>> print fs.render()
<div>
 <label class="field_opt" for="foo">
  Foo
 </label>
 <input id="foo" name="foo" type="text" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("foo").focus();
//]]>
</script>
<div>
 <label class="field_req" for="id">
  Id
 </label>
 <input id="id" name="id" type="text" />
</div>

>>> fs = FieldSet(Two)
>>> print fs.render()
<div>
 <label class="field_opt" for="foo">
  Foo
 </label>
 <input id="foo" name="foo" type="text" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("foo").focus();
//]]>
</script>

>>> fs = FieldSet(Two)
>>> fs.configure(options=[fs.foo.label('A custom label')])
>>> print fs.render()
<div>
 <label class="field_opt" for="foo">
  A custom label
 </label>
 <input id="foo" name="foo" type="text" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("foo").focus();
//]]>
</script>

>>> fs = FieldSet(Two)
>>> assert fs.render() == configure_and_render(fs, include=[fs.foo])
>>> assert fs.render() == configure_and_render(fs, exclude=[fs.id])

>>> fs = FieldSet(Two) 
>>> fs.configure(include=[fs.foo.hidden()])
>>> print fs.render()
<input id="foo" name="foo" type="hidden" />

>>> fs = FieldSet(Two)
>>> fs.configure(include=[fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')])])
>>> print fs.render()
<div>
 <label class="field_opt" for="foo">
  Foo
 </label>
 <select id="foo" name="foo">
  <option value="value1">
   option1
  </option>
  <option value="value2">
   option2
  </option>
 </select>
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("foo").focus();
//]]>
</script>

>>> fs = FieldSet(Two)
>>> assert configure_and_render(fs, include=[fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')])]) == configure_and_render(fs, options=[fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')])]) 

>>> fs = FieldSet(Two)
>>> print fs.foo.render(onblur='test()')
<input id="foo" name="foo" onblur="test()" type="text" />
>>> cb = Checkbox()
>>> fs = FieldSet(cb)
>>> print fs.field.render()
<input id="field" name="field" type="checkbox" value="True" />
>>> print fs.field.dropdown().render()
<select id="field" name="field"><option value="True">True</option>
<option value="False">False</option></select>
>>> fs.validate()
True
>>> fs.errors
{}
>>> fs.sync()
>>> cb.field
False
>>> fs.rebind(data={'field': 'true'})
>>> fs.validate()
True
>>> fs.sync()
>>> cb.field
True

>>> fs = FieldSet(Two)
>>> print fs.foo.dropdown(options=['one', 'two']).radio().render() 
<input id="foo_one" name="foo" type="radio" value="one" />one<br /><input id="foo_two" name="foo" type="radio" value="two" />two
>>> assert fs.foo.radio(options=['one', 'two']).render() == fs.foo.dropdown(options=['one', 'two']).radio().render()
>>> print fs.foo.radio(options=['one', 'two']).dropdown().render()
<select id="foo" name="foo"><option value="one">one</option>
<option value="two">two</option></select>
>>> assert fs.foo.dropdown(options=['one', 'two']).render() == fs.foo.radio(options=['one', 'two']).dropdown().render()
>>> print fs.foo.dropdown(options=['one', 'two'], multiple=True).checkbox().render() 
<input id="foo" name="foo" type="checkbox" value="one" />one<br /><input id="foo" name="foo" type="checkbox" value="two" />two

>>> fs = FieldSet(User, session)
>>> print fs.render()
<div>
 <label class="field_req" for="email">
  Email
 </label>
 <input id="email" maxlength="40" name="email" type="text" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("email").focus();
//]]>
</script>
<div>
 <label class="field_opt" for="name">
  Name
 </label>
 <input id="name" maxlength="30" name="name" type="text" />
</div>
<div>
 <label class="field_opt" for="orders">
  Orders
 </label>
 <select id="orders" multiple="multiple" name="orders" size="5">
  <option value="1">
   Quantity: 10
  </option>
  <option value="2">
   Quantity: 5
  </option>
 </select>
</div>
<div>
 <label class="field_req" for="password">
  Password
 </label>
 <input id="password" maxlength="20" name="password" type="text" />
</div>

>>> fs = FieldSet(bill)
>>> print fs.orders.render()
<select id="orders" multiple="multiple" name="orders" size="5"><option value="1" selected="selected">Quantity: 10</option>
<option value="2">Quantity: 5</option></select>
>>> print fs.orders.radio().render()
<input id="orders_1" name="orders" type="radio" value="1" />Quantity: 10<br /><input id="orders_2" name="orders" type="radio" value="2" />Quantity: 5
>>> print fs.orders.radio(options=query_options(session.query(Order).filter_by(id=1))).render()
<input id="orders_1" name="orders" type="radio" value="1" />Quantity: 10

>>> fs = FieldSet(Two)
>>> print fs.foo.render()
<input id="foo" name="foo" type="text" />

>>> fs = FieldSet(Two)
>>> print fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')]).render()
<select id="foo" name="foo"><option value="value1">option1</option>
<option value="value2">option2</option></select>

>>> fs = FieldSet(Order, session)
>>> print fs.render()
<div>
 <label class="field_req" for="quantity">
  Quantity
 </label>
 <input id="quantity" name="quantity" type="text" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("quantity").focus();
//]]>
</script>
<div>
 <label class="field_req" for="user_id">
  User
 </label>
 <select id="user_id" name="user_id">
  <option value="1">
   Bill
  </option>
  <option value="2">
   John
  </option>
 </select>
</div>

# this seems particularly prone to errors; break it out in its own test
>>> fs = FieldSet(order1)
>>> fs.user.value
1

# test re-binding
>>> fs = FieldSet(Order)
>>> fs.configure(pk=True, options=[fs.quantity.hidden()])
>>> fs.rebind(order1)
>>> fs.quantity.value
10
>>> fs.session == object_session(order1)
True
>>> print fs.render()
<div>
 <label class="field_req" for="id">
  Id
 </label>
 <input id="id" name="id" type="text" value="1" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("id").focus();
//]]>
</script>
<input id="quantity" name="quantity" type="hidden" value="10" />
<div>
 <label class="field_req" for="user_id">
  User
 </label>
 <select id="user_id" name="user_id">
  <option value="1" selected="selected">
   Bill
  </option>
  <option value="2">
   John
  </option>
 </select>
</div>

>>> fs = FieldSet(One)
>>> fs.configure(pk=True)
>>> print fs.render()
<div>
 <label class="field_req" for="id">
  Id
 </label>
 <input id="id" name="id" type="text" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("id").focus();
//]]>
</script>
>>> fs.configure(include=[])
>>> print fs.render()
<BLANKLINE>
>>> fs.configure(pk=True, focus=None)
>>> print fs.render()
<div>
 <label class="field_req" for="id">
  Id
 </label>
 <input id="id" name="id" type="text" />
</div>

>>> fs = FieldSet(One)
>>> fs.rebind(Two) #doctest: +ELLIPSIS
Traceback (most recent call last):
...
ValueError: ...

>>> fs = FieldSet(Two)
>>> fs.configure()
>>> fs2 = fs.bind(Two)
>>> [fs2 == attr.parent for attr in fs2._render_fields]
[True]

# tables
>>> t = Table(bill)
>>> print t.render().strip()
<table>
  <caption>User</caption>
  <tbody>
    <tr>
      <th>Email</th>
      <td>bill@example.com</td>
    </tr>
    <tr>
      <th>Name</th>
      <td>Bill</td>
    </tr>
    <tr>
      <th>Orders</th>
      <td>Quantity: 10</td>
    </tr>
    <tr>
      <th>Password</th>
      <td>1234</td>
    </tr>
  </tbody>
</table>

>>> t = TableCollection([bill])
>>> print t.render().strip()
<table>
  <caption>Nonetype (1)</caption>
  <thead>
    <tr>
      <th>Email</th>
      <th>Name</th>
      <th>Orders</th>
      <th>Password</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>bill@example.com</td>
      <td>Bill</td>
      <td>Quantity: 10</td>
      <td>1234</td>
    </tr>
  </tbody>
</table>

>>> fs = FieldSet(OTOParent, session)
>>> print fs.render()
<div>
 <label class="field_req" for="oto_child_id">
  Child
 </label>
 <select id="oto_child_id" name="oto_child_id">
 </select>
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("oto_child_id").focus();
//]]>
</script>

# validation + sync
>>> two = Two()
>>> fs = FieldSet(two, data={'foo': ''})
>>> fs.configure(options=[fs.foo.required()], focus=None)
>>> fs.validate()
False
>>> fs.errors
{AttributeField(foo): ['Please enter a value']}
>>> print fs.render()
<div>
 <label class="field_req" for="foo">
  Foo
 </label>
 <input id="foo" name="foo" type="text" value="" />
 <span class="field_error">
  Please enter a value
 </span>
</div>
>>> fs.rebind(two, data={'foo': 'asdf'})
>>> fs.data
{'foo': 'asdf'}
>>> fs.validate()
True
>>> fs.errors
{}
>>> fs.sync()
>>> two.foo
'asdf'

>>> one = One()
>>> fs = FieldSet(one, data={'id': 1})
>>> fs.configure(pk=True)
>>> fs.validate()
True
>>> fs.sync()
>>> one.id
1
>>> fs.rebind(one, data={'id': 'asdf'})
>>> fs.validate()
False
>>> fs.errors
{AttributeField(id): [ValidationException('Value is not an integer',)]}

>>> fs = FieldSet(User, data={'orders': []})
>>> fs.configure(include=[fs.orders])
>>> fs.validate()
True
>>> fs.sync()
>>> fs.model.orders
[]
>>> fs.rebind(User, session, {'orders': [str(order1.id), str(order2.id)]})
>>> fs.validate()
True
>>> fs.sync()
>>> fs.model.orders == [order1, order2]
True
>>> session.rollback()

>>> fs = FieldSet(Three, data={'foo': 'asdf', 'bar': 'fdsa'})
>>> def custom_validator(data):
...   if data['foo'] != data['bar']:
...     raise ValidationException('foo and bar do not match')
>>> fs.configure(global_validator=custom_validator, focus=None)
>>> fs.validate()
False
>>> fs.errors
{None: ('foo and bar do not match',)}
>>> print fs.render()
<div class="fieldset_error">
 foo and bar do not match
</div>
<div>
 <label class="field_opt" for="bar">
  Bar
 </label>
 <input id="bar" name="bar" type="text" value="fdsa" />
</div>
<div>
 <label class="field_opt" for="foo">
  Foo
 </label>
 <input id="foo" name="foo" type="text" value="asdf" />
</div>

# natural PKs
>>> fs = FieldSet(NaturalOrder, session)
>>> print fs.render()
<div>
 <label class="field_req" for="quantity">
  Quantity
 </label>
 <input id="quantity" name="quantity" type="text" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("quantity").focus();
//]]>
</script>
<div>
 <label class="field_req" for="user_email">
  User
 </label>
 <select id="user_email" name="user_email">
  <option value="nbill@example.com">
   Natural Bill
  </option>
  <option value="njohn@example.com">
   Natural John
  </option>
 </select>
</div>
>>> fs.rebind(norder2, session, {'user_email': nbill.email})
>>> fs.sync()
>>> fs.model.user_email == nbill.email
True

# allow attaching custom attributes to wrappers
>>> fs = FieldSet(User)
>>> fs.name.baz = 'asdf'
>>> fs2 = fs.bind(bill)
>>> fs2.name.baz
'asdf'

# Field
>>> fs = FieldSet(One)
>>> fs.add(Field('foo'))
>>> print configure_and_render(fs, focus=None)
<div>
 <label class="field_opt" for="foo">
  Foo
 </label>
 <input id="foo" name="foo" type="text" />
</div>

>>> fs = FieldSet(One)
>>> fs.add(Field('foo', types.Integer, value=2))
>>> fs.foo.value
2
>>> print configure_and_render(fs, focus=None)
<div>
 <label class="field_opt" for="foo">
  Foo
 </label>
 <input id="foo" name="foo" type="text" value="2" />
</div>
>>> fs.rebind(One, data={'foo': 4})
>>> fs.sync()
>>> fs.foo.value
4

>>> fs = FieldSet(One)
>>> fs.add(Field('foo', types.Integer, value=2).dropdown(options=[('1', 1), ('2', 2)]))
>>> print configure_and_render(fs, focus=None)
<div>
 <label class="field_opt" for="foo">
  Foo
 </label>
 <select id="foo" name="foo">
  <option value="1">
   1
  </option>
  <option value="2" selected="selected">
   2
  </option>
 </select>
</div>

# test Field __hash__, __eq__
>>> fs.foo == fs.foo.dropdown(options=[('1', 1), ('2', 2)])
True
>>> fs2 = FieldSet(One)
>>> fs2.add(Field('foo', types.Integer, value=2))
>>> fs2.configure(options=[fs2.foo.dropdown(options=[('1', 1), ('2', 2)])], focus=None)
>>> fs.render() == fs2.render()
True

>>> fs = FieldSet(One)
>>> fs.add(Field('foo', types.Integer, value=[2, 3]).dropdown(options=[('1', 1), ('2', 2), ('3', 3)], multiple=True))
>>> print configure_and_render(fs, focus=None)
<div>
 <label class="field_opt" for="foo">
  Foo
 </label>
 <select id="foo" multiple="multiple" name="foo" size="5">
  <option value="1">
   1
  </option>
  <option value="2" selected="selected">
   2
  </option>
  <option value="3" selected="selected">
   3
  </option>
 </select>
</div>
>>> fs.rebind(One, data={'foo': ['1', '2']})
>>> fs.sync()
>>> fs.foo.value
[1, 2]

# test attribute names
>>> fs = FieldSet(One)
>>> fs.add(Field('foo'))
>>> fs.foo == fs.fields['foo']
True
>>> fs.add(Field('add'))
>>> fs.add == fs.fields['add']
False

"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()
