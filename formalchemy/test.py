from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base, declared_synonym

engine = create_engine('sqlite://')
Base = declarative_base(engine)

class One(Base):
    __tablename__ = 'ones'
    id = Column('id', Integer, primary_key=True)
one = One()

class Two(Base):
    __tablename__ = 'twos'
    id = Column('id', Integer, primary_key=True)
    foo = Column('foo', Unicode, nullable=False)
two = Two()

class Checkbox(Base):
    __tablename__ = 'checkboxes'
    id = Column('id', Integer, primary_key=True)
    field = Column('field', Boolean, nullable=False)
checkbox = Checkbox()

class Order(Base):
    __tablename__ = 'orders'
    id = Column('id', Integer, primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('users.id'))
    quantity = Column('quantity', Integer, nullable=False)

class User(Base):
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key=True)
    email = Column('email', Unicode(40), unique=True, nullable=False)
    password = Column('password', Unicode(20), nullable=False)
    first_name = Column('first_name', Unicode(20))
    last_name = Column('last_name', Unicode(20))
    description = Column('description', Unicode)
    active = Column('active', Boolean, default=True)
    orders = relation(Order, backref='user')

user = User()


from forms import FieldSet, Field

__doc__ = r"""
>>> fs = FieldSet(one)
>>> print fs.render()
<fieldset>
  <legend>One</legend>
  <div>
    <label class="field_req" for="id">Id</label>
    <input id="id" name="id" type="text" />
  </div>
  <script type="text/javascript">
  //<![CDATA[
  document.getElementById("id").focus();
  //]]>
  </script>
</fieldset>

>>> fs = FieldSet(two)
>>> print fs.render()
<fieldset>
  <legend>Two</legend>
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
</fieldset>

>>> fs = FieldSet(two)
>>> print fs.render(pk=False)
<fieldset>
  <legend>Two</legend>
  <div>
    <label class="field_req" for="foo">Foo</label>
    <input id="foo" name="foo" type="text" />
  </div>
  <script type="text/javascript">
  //<![CDATA[
  document.getElementById("foo").focus();
  //]]>
  </script>
</fieldset>

>>> fs = FieldSet(two)
>>> assert fs.render(pk=False) == fs.render(include=[Two.foo])
>>> assert fs.render(pk=False) == fs.render(exclude=[Two.id])

>>> fs = FieldSet(two) 
>>> print fs.render(pk=False, hidden=[Two.foo]) # todo fix this

>>> fs = FieldSet(two)
>>> print fs.render(pk=False, dropdowns={Two.foo: [('option1', 'value1'), ('option2', 'value2')]})

>>> fs = FieldSet(checkbox)
>>> print fs.render(pk=False)
<fieldset>
  <legend>Checkbox</legend>
  <div>
    <label class="field_req" for="field">Field</label>
    <input id="field" name="field" type="checkbox" value="True" /><input id="field" name="field" type="hidden" value="False" />
  </div>
  <script type="text/javascript">
  //<![CDATA[
  document.getElementById("field").focus();
  //]]>
  </script>
</fieldset>

>>> fs = FieldSet(user)
>>> print fs.render()
<fieldset>
  <legend>User</legend>
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
</fieldset>
"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()
