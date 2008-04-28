import logging
logging.basicConfig(level=logging.DEBUG)

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base, declared_synonym
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)

engine = create_engine('sqlite://')
Session = scoped_session(sessionmaker(autoflush=True, bind=engine))
Base = declarative_base(engine)

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

class Order(Base):
    __tablename__ = 'orders'
    id = Column('id', Integer, primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('users.id'), nullable=False)
    quantity = Column('quantity', Integer, nullable=False)

class User(Base):
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key=True)
    email = Column('email', Unicode(40), unique=True, nullable=False)
    password = Column('password', Unicode(20), nullable=False)
    first_name = Column('first_name', Unicode(20))
    last_name = Column('last_name', Unicode(20))
    description = Column('description', Text)
    active = Column('active', Boolean, default=True)
    orders = relation(Order, backref='user')
    def __str__(self):
        return self.first_name + ' ' + self.last_name
    
Base.metadata.create_all()
# test w/ explicit session to avoid cluttering up implicit one w/ throwaway object creations
session = Session()

bill = User(email='bill@example.com', 
            password='1234',
            first_name='Bill',
            last_name='Jones',
            description='boring description')
session.save(bill)
session.flush() # will update bill w/ id

order1 = Order(user=bill, quantity=10)
session.save(order1)

session.commit()


from forms import FieldSet, Field
from tables import Table, TableCollection

__doc__ = r"""
# some low-level testing first
>>> fs = FieldSet(order1)
>>> list(sorted(fs._raw_attrs(), key=lambda attr:attr.name))
[AttributeWrapper(id), AttributeWrapper(quantity), AttributeWrapper(user_id), AttributeWrapper(user)]

>>> fs = FieldSet(bill)
>>> list(sorted(fs._raw_attrs(), key=lambda attr:attr.name))
[AttributeWrapper(active), AttributeWrapper(description), AttributeWrapper(email), AttributeWrapper(first_name), AttributeWrapper(id), AttributeWrapper(last_name), AttributeWrapper(password), AttributeWrapper(orders)]

>>> fs = FieldSet(One())
>>> print fs.render()
<div>
  <label class="field_req" for="id">Id</label>
  <input id="id" name="id" type="text" />
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("id").focus();
//]]>
</script>

>>> fs = FieldSet(Two())
>>> print fs.render()
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

>>> fs = FieldSet(Two())
>>> print fs.render(pk=False)
<div>
  <label class="field_req" for="foo">Foo</label>
  <input id="foo" name="foo" type="text" />
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("foo").focus();
//]]>
</script>

>>> fs = FieldSet(Two())
>>> assert fs.render(pk=False) == fs.render(include=[fs.foo])
>>> assert fs.render(pk=False) == fs.render(exclude=[fs.id])

>>> fs = FieldSet(Two()) 
>>> print fs.render(include=[fs.foo.hidden()])
<input id="foo" name="foo" type="hidden" />

>>> fs = FieldSet(Two())
>>> print fs.render(include=[fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')])])
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

>>> fs = FieldSet(Two())
>>> assert fs.render(include=[fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')])]) == fs.render(pk=False, options=[fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')])]) 

>>> fs = FieldSet(Checkbox())
>>> print fs.render(pk=False)
<div>
  <label class="field_req" for="field">Field</label>
  <input id="field" name="field" type="checkbox" value="True" /><input id="field" name="field" type="hidden" value="False" />
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("field").focus();
//]]>
</script>

>>> fs = FieldSet(User())
>>> print fs.render()
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
  <label class="field_opt" for="description">Description</label>
  <input id="description" name="description" type="text" />
</div>
<div>
  <label class="field_req" for="email">Email</label>
  <input id="email" maxlength="40" name="email" type="text" />
</div>
<div>
  <label class="field_opt" for="first_name">First name</label>
  <input id="first_name" maxlength="20" name="first_name" type="text" />
</div>
<div>
  <label class="field_req" for="id">Id</label>
  <input id="id" name="id" type="text" />
</div>
<div>
  <label class="field_opt" for="last_name">Last name</label>
  <input id="last_name" maxlength="20" name="last_name" type="text" />
</div>
<div>
  <label class="field_req" for="password">Password</label>
  <input id="password" maxlength="20" name="password" type="text" />
</div>

>>> fs = FieldSet(Two())
>>> print fs.foo.render()
<input id="foo" name="foo" type="text" />

>>> fs = FieldSet(Two())
>>> print fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')]).render()
<select id="foo" name="foo"><option value="value1">option1</option>
<option value="value2">option2</option></select>

>>> fs = FieldSet(Order(), session)
>>> print fs.render()
<div>
  <label class="field_req" for="id">Id</label>
  <input id="id" name="id" type="text" />
</div>
<script type="text/javascript">
//<![CDATA[
document.getElementById("id").focus();
//]]>
</script>
<div>
  <label class="field_req" for="quantity">Quantity</label>
  <input id="quantity" name="quantity" type="text" />
</div>
<div>
  <label class="field_req" for="user_id">User id</label>
  <select id="user_id" name="user_id"><option value="1">Bill Jones</option></select>
</div>

# test re-binding
>>> fs = FieldSet(Order(), session)
>>> fs.quantity = fs.quantity.hidden()
>>> fs.bind(order1)
>>> print fs.render() # should render w/ current selection the default.
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
  <label class="field_req" for="user_id">User id</label>
  <select id="user_id" name="user_id"><option value="1" selected="selected">Bill Jones</option></select>
</div>

>>> t = Table(bill)
>>> print t.render()
<table>
  <caption>User</caption>
  <tbody>
    <tr>
      <th>Active</th>
      <td><em>True</em></td>
    </tr>
    <tr>
      <th>Description</th>
      <td>boring description</td>
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
      <th>Id</th>
      <td>1</td>
    </tr>
    <tr>
      <th>Last name</th>
      <td>Jones</td>
    </tr>
    <tr>
      <th>Password</th>
      <td>1234</td>
    </tr>
  </tbody>
</table>

>>> t = TableCollection([bill])
>>> print t.render()
<table>
  <caption>Nonetype (1)</caption>
  <thead>
    <tr>
      <th>Active</th>
      <th>Description</th>
      <th>Email</th>
      <th>First name</th>
      <th>Id</th>
      <th>Last name</th>
      <th>Password</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><em>True</em></td>
      <td>boring description</td>
      <td>bill@example.com</td>
      <td>Bill</td>
      <td>1</td>
      <td>Jones</td>
      <td>1234</td>
    </tr>
  </tbody>
</table>
"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()
