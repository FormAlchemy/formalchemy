import logging
logging.basicConfig(level=logging.DEBUG)

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base, declared_synonym
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
    foo = Column('foo', Text, nullable=False)

class Checkbox(Base):
    __tablename__ = 'checkboxes'
    id = Column('id', Integer, primary_key=True)
    field = Column('field', Boolean, nullable=False)

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
    active = Column('active', Boolean, default=True)
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


def _unwhitespace(st):
    import re
    return re.sub(r'''\n\s*\n''', '\n', st).strip()


from forms import FieldSet
from tables import Table, TableCollection

__doc__ = r"""
# some low-level testing first
>>> fs = FieldSet(order1)
>>> list(sorted(fs._raw_attrs(), key=lambda attr: attr.key))
[AttributeWrapper(id), AttributeWrapper(quantity), AttributeWrapper(user), AttributeWrapper(user_id)]

>>> fs = FieldSet(bill)
>>> list(sorted(fs._raw_attrs(), key=lambda attr: attr.key))
[AttributeWrapper(active), AttributeWrapper(email), AttributeWrapper(first_name), AttributeWrapper(id), AttributeWrapper(last_name), AttributeWrapper(orders), AttributeWrapper(password)]

>>> fs = FieldSet(One)
>>> print _unwhitespace(fs.render(pk=True))
<div>
  <label class="field_req" for="id">Id</label>
  <input id="id" name="id" type="text" />
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("id").focus();
//]]>
</script>

>>> fs = FieldSet(Two)
>>> print _unwhitespace(fs.render(pk=True))
<div>
  <label class="field_req" for="foo">Foo</label>
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
>>> print _unwhitespace(fs.render())
<div>
  <label class="field_req" for="foo">Foo</label>
  <input id="foo" name="foo" type="text" />
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("foo").focus();
//]]>
</script>

>>> fs = FieldSet(Two)
>>> print _unwhitespace(fs.render(options=[fs.foo.label('A custom label')]))
<div>
  <label class="field_req" for="foo">A custom label</label>
  <input id="foo" name="foo" type="text" />
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("foo").focus();
//]]>
</script>

>>> fs = FieldSet(Two)
>>> assert fs.render(pk=False) == fs.render(include=[fs.foo])
>>> assert fs.render(pk=False) == fs.render(exclude=[fs.id])

>>> fs = FieldSet(Two) 
>>> print _unwhitespace(fs.render(include=[fs.foo.hidden()]))
<input id="foo" name="foo" type="hidden" />

>>> fs = FieldSet(Two)
>>> print _unwhitespace(fs.render(include=[fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')])]))
<div>
  <label class="field_req" for="foo">Foo</label>
  <select id="foo" name="foo"><option value="value1">option1</option>
<option value="value2">option2</option></select>
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("foo").focus();
//]]>
</script>

>>> fs = FieldSet(Two)
>>> assert fs.render(include=[fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')])]) == fs.render(options=[fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')])]) 

>>> fs = FieldSet(Checkbox)
>>> print _unwhitespace(fs.render())
<div>
  <label class="field_req" for="field">Field</label>
  <input id="field" name="field" type="checkbox" value="True" /><input id="field" name="field" type="hidden" value="False" />
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("field").focus();
//]]>
</script>

>>> fs = FieldSet(User, session)
>>> print _unwhitespace(fs.render())
<div>
  <label class="field_opt" for="active">Active</label>
  <input checked="checked" id="active" name="active" type="checkbox" value="True" /><input id="active" name="active" type="hidden" value="False" />
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("active").focus();
//]]>
</script>
<div>
  <label class="field_req" for="email">Email</label>
  <input id="email" maxlength="40" name="email" type="text" />
</div>
<div>
  <label class="field_opt" for="first_name">First name</label>
  <input id="first_name" maxlength="20" name="first_name" type="text" />
</div>
<div>
  <label class="field_opt" for="last_name">Last name</label>
  <input id="last_name" maxlength="20" name="last_name" type="text" />
</div>
<div>
  <label class="field_req" for="orders">Orders</label>
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

>>> fs = FieldSet(Two)
>>> print fs.foo.render()
<input id="foo" name="foo" type="text" />

>>> fs = FieldSet(Two)
>>> print fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')]).render()
<select id="foo" name="foo"><option value="value1">option1</option>
<option value="value2">option2</option></select>

>>> fs = FieldSet(Order, session)
>>> print _unwhitespace(fs.render())
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
>>> fs.quantity = fs.quantity.hidden()
>>> fs.rebind(order1)
>>> fs.session == object_session(order1)
True
>>> print _unwhitespace(fs.render(pk=True)) # should render w/ current selection the default.)
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
>>> print _unwhitespace(fs.render())
<div>
  <label class="field_req" for="id">Id</label>
  <input id="id" name="id" type="text" />
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("id").focus();
//]]>
</script>
>>> fs.reconfigure(include=[])
>>> print _unwhitespace(fs.render())
<BLANKLINE>

>>> fs = FieldSet(One)
>>> fs.rebind(Two)
Traceback (most recent call last):
...
ValueError: You can only bind to another object of the same type you originally bound to (<class '__main__.One'>), not <class '__main__.Two'>

# tables
>>> t = Table(bill)
>>> print _unwhitespace(t.render())
<table>
  <caption>User</caption>
  <tbody>
    <tr>
      <th>Active</th>
      <td>True</td>
    </tr>
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
>>> print _unwhitespace(t.render())
<table>
  <caption>Nonetype (1)</caption>
  <thead>
    <tr>
      <th>Active</th>
      <th>Email</th>
      <th>First name</th>
      <th>Last name</th>
      <th>Orders</th>
      <th>Password</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>True</td>
      <td>bill@example.com</td>
      <td>Bill</td>
      <td>Jones</td>
      <td>Quantity: 10</td>
      <td>1234</td>
    </tr>
  </tbody>
</table>

>>> fs = FieldSet(OTOParent, session)
>>> print _unwhitespace(fs.render())
<div>
  <label class="field_req" for="oto_child_id">Child</label>
  <select id="oto_child_id" name="oto_child_id"></select>
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("oto_child_id").focus();
//]]>
</script>

"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()
