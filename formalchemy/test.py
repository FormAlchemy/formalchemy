import logging
logging.basicConfig(level=logging.DEBUG)

from sqlalchemy import *
from sqlalchemy.orm import *
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
# probably need to add _render_as attr and check
# isinstance(getattr(myclass, '_render_as', type(myclass)), Boolean)
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
    first_name = Column('first_name', Unicode(20))
    last_name = Column('last_name', Unicode(20))
    orders = relation(Order, backref='user')
    def __str__(self):
        return self.first_name + ' ' + self.last_name
    
Base.metadata.create_all()

session = Session()

bill = User(email='bill@example.com', 
            password='1234',
            first_name='Bill',
            last_name='Jones')
john = User(email='john@example.com', 
            password='5678',
            first_name='John',
            last_name='Kerry')

order1 = Order(user=bill, quantity=10)
order2 = Order(user=john, quantity=5)

session.commit()


from forms import FieldSet
from fields import query_options
from validators import ValidationException
from tables import Table, TableCollection

def configure_and_render(fs, **options):
    fs.configure(**options)
    return fs.render()

__doc__ = r"""
# some low-level testing first
>>> fs = FieldSet(order1)
>>> list(sorted(fs._raw_attrs(), key=lambda attr: attr.key))
[AttributeWrapper(id), AttributeWrapper(quantity), AttributeWrapper(user), AttributeWrapper(user_id)]

>>> fs = FieldSet(bill)
>>> list(sorted(fs._raw_attrs(), key=lambda attr: attr.key))
[AttributeWrapper(email), AttributeWrapper(first_name), AttributeWrapper(id), AttributeWrapper(last_name), AttributeWrapper(orders), AttributeWrapper(password)]

>>> fs = FieldSet(One)
>>> fs.configure(pk=True, focus=None)
>>> fs.id.is_required()
True
>>> print fs.render().strip()
<div>
  <label class="field_req" for="id">Id</label>
  <input id="id" name="id" type="text" />
</div>

>>> fs = FieldSet(Two)
>>> fs.configure(pk=True)
>>> print fs.render().strip()
<div>
  <label class="field_opt" for="foo">Foo</label>
  <input id="foo" name="foo" type="text" />
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("foo").focus();
//]]>
</script>
<div>
  <label class="field_req" for="id">Id</label>
  <input id="id" name="id" type="text" />
</div>

>>> fs = FieldSet(Two)
>>> print fs.render().strip()
<div>
  <label class="field_opt" for="foo">Foo</label>
  <input id="foo" name="foo" type="text" />
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("foo").focus();
//]]>
</script>

>>> fs = FieldSet(Two)
>>> fs.configure(options=[fs.foo.label('A custom label')])
>>> print fs.render().strip()
<div>
  <label class="field_opt" for="foo">A custom label</label>
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
>>> print fs.render().strip()
<input id="foo" name="foo" type="hidden" />

>>> fs = FieldSet(Two)
>>> fs.configure(include=[fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')])])
>>> print fs.render().strip()
<div>
  <label class="field_opt" for="foo">Foo</label>
  <select id="foo" name="foo"><option value="value1">option1</option>
<option value="value2">option2</option></select>
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
>>> print fs.render().strip()
<div>
  <label class="field_req" for="field">Field</label>
  <input id="field" name="field" type="checkbox" value="True" />
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("field").focus();
//]]>
</script>
>>> fs.validate()
True
>>> fs.errors()
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

>>> fs = FieldSet(User, session)
>>> print fs.render().strip()
<div>
  <label class="field_req" for="email">Email</label>
  <input id="email" maxlength="40" name="email" type="text" />
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("email").focus();
//]]>
</script>
<div>
  <label class="field_opt" for="first_name">First name</label>
  <input id="first_name" maxlength="20" name="first_name" type="text" />
</div>
<div>
  <label class="field_opt" for="last_name">Last name</label>
  <input id="last_name" maxlength="20" name="last_name" type="text" />
</div>
<div>
  <label class="field_opt" for="orders">Orders</label>
  <select id="orders" multiple="multiple" name="orders" size="5"><option value="1">Quantity: 10</option>
<option value="2">Quantity: 5</option></select>
</div>
<div>
  <label class="field_req" for="password">Password</label>
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
>>> print fs.render().strip()
<div>
  <label class="field_req" for="quantity">Quantity</label>
  <input id="quantity" name="quantity" type="text" />
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("quantity").focus();
//]]>
</script>
<div>
  <label class="field_req" for="user_id">User</label>
  <select id="user_id" name="user_id"><option value="1">Bill Jones</option>
<option value="2">John Kerry</option></select>
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
>>> print fs.render().strip() # should render w/ current selection the default
<div>
  <label class="field_req" for="id">Id</label>
  <input id="id" name="id" type="text" value="1" />
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("id").focus();
//]]>
</script>
<input id="quantity" name="quantity" type="hidden" value="10" />
<div>
  <label class="field_req" for="user_id">User</label>
  <select id="user_id" name="user_id"><option value="1" selected="selected">Bill Jones</option>
<option value="2">John Kerry</option></select>
</div>

>>> fs = FieldSet(One)
>>> fs.configure(pk=True)
>>> print fs.render().strip()
<div>
  <label class="field_req" for="id">Id</label>
  <input id="id" name="id" type="text" />
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("id").focus();
//]]>
</script>
>>> fs.configure(include=[])
>>> print fs.render().strip()
<BLANKLINE>
>>> fs.configure(pk=True, focus=None)
>>> print fs.render().strip()
<div>
  <label class="field_req" for="id">Id</label>
  <input id="id" name="id" type="text" />
</div>

>>> fs = FieldSet(One)
>>> fs.rebind(Two)
Traceback (most recent call last):
...
ValueError: You can only bind to another object of the same type you originally bound to (<class '__main__.One'>), not <class '__main__.Two'>

>>> fs = FieldSet(Two)
>>> fs.configure()
>>> fs2 = fs.bind(Two)
>>> [fs2 == attr.parent for attr in fs2._render_attrs]
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
      <th>First name</th>
      <td>Bill</td>
    </tr>
    <tr>
      <th>Last name</th>
      <td>Jones</td>
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
      <th>First name</th>
      <th>Last name</th>
      <th>Orders</th>
      <th>Password</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>bill@example.com</td>
      <td>Bill</td>
      <td>Jones</td>
      <td>Quantity: 10</td>
      <td>1234</td>
    </tr>
  </tbody>
</table>

>>> fs = FieldSet(OTOParent, session)
>>> print fs.render().strip()
<div>
  <label class="field_req" for="oto_child_id">Child</label>
  <select id="oto_child_id" name="oto_child_id"></select>
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
>>> fs.errors()
{AttributeWrapper(foo): ['Please enter a value']}
>>> print fs.render().strip()
<div>
  <label class="field_req" for="foo">Foo</label>
  <input id="foo" name="foo" type="text" value="" />
  <span class="field_error">Please enter a value</span>
</div>
>>> fs.rebind(two, data={'foo': 'asdf'})
>>> fs.data
{'foo': 'asdf'}
>>> fs.validate()
True
>>> fs.errors()
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
>>> fs.errors()
{AttributeWrapper(id): [ValidationException('Value is not an integer',)]}

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

>>> fs = FieldSet(Three, data={'foo': 'asdf', 'bar': 'fdsa'})
>>> def custom_validator(data):
...   if data['foo'] != data['bar']:
...     raise ValidationException('foo and bar do not match')
>>> fs.configure(global_validator=custom_validator, focus=None)
>>> fs.validate()
False
>>> fs.errors()
{None: ('foo and bar do not match',)}
>>> print fs.render().strip()
<div class="fieldset_error">
  foo and bar do not match
</div>
<div>
  <label class="field_opt" for="bar">Bar</label>
  <input id="bar" name="bar" type="text" value="fdsa" />
</div>
<div>
  <label class="field_opt" for="foo">Foo</label>
  <input id="foo" name="foo" type="text" value="asdf" />
</div>

# allow attaching custom attributes to wrappers
>>> fs = FieldSet(User)
>>> fs.first_name.baz = 'asdf'
>>> fs2 = fs.bind(bill)
>>> fs2.first_name.baz
'asdf'
"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()
