# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from formalchemy.tables import *
from formalchemy.forms import *
from formalchemy.fields import *
from formalchemy.validators import ValidationError
import formalchemy.validators as validators

__all__ = ["FieldSet", "AbstractFieldSet", "Field", "FieldRenderer", "Table", "TableCollection", "Grid", "form_data", "query_options", "ValidationError", "validators"]
__version__ = "0.3"

__doc__ = """
=Introduction=

!FormAlchemy greatly speeds development with SQLAlchemy mapped classes (models)
in a HTML forms environment.

!FormAlchemy eliminates boilerplate by autogenerating HTML input
fields from a given model. !FormAlchemy will try to figure out what
kind of HTML code should be returned by introspecting the model's
properties and generate ready-to-use HTML code that will fit the
developer's application.

Of course, !FormAlchemy can't figure out everything,
i.e, the developer might want to display only a few columns from the given
model. Thus, !FormAlchemy is also highly customizable.


=Features=

  * Generates HTML form fields from SQLAlchemy mapped classes or manually added Fields
  * Handles object relationships (including many-to-many), not just simple data types
  * Pre-fills input fields with current or default value
  * Highly customizable HTML output
  * Validates input and displays errors in-line
  * Syncs model instances with input data
  * Easy-to-use API
  * SQLAlchemy 0.4 (0.4.1 or later) and 0.5 compatible
  * Elixir compatible (?)
  
  
=Limitations=

  * Currently, !FormAlchemy only handles single-valued (not composite) primary and foreign keys


=Installation=

Check out the instructions for InstallingFormAlchemy.


=Full Documentation=

!FormAlchemy's documentation is available [http://code.google.com/p/formalchemy/wiki/FormAlchemyDocumentation03 here].


=Copyright and License=

Copyright (C) 2007 Alexandre Conrad, aconard(dot.)tlv(at@)magic(dot.)fr

!FormAlchemy is released under the 
[http://www.opensource.org/licenses/mit-license.php MIT License].


=Quickstart=

To get started, you only need to know about one class, `FieldSet`, and a
handful of methods:

  * `render`: returns a string containing the form input html
  * `validate`: true if the form passes its validations; otherwise, false
  * `sync`: syncs the model instance that was bound to the input data

This quickstart illustrates these four methods. For full details on
customizing `FieldSet` behavior, see FormAlchemyDocumentation03.

We'll start with two simple SQLAlchemy models with a one-to-many relationship
(each User can have many Orders):

{{{
>>> from sqlalchemy import *
>>> from sqlalchemy.orm import *
>>> from sqlalchemy.ext.declarative import declarative_base
>>> engine = create_engine('sqlite://')
>>> Session = scoped_session(sessionmaker(autoflush=True, bind=engine))
>>> Base = declarative_base(engine, mapper=Session.mapper)

>>> class Order(Base):
...     __tablename__ = 'orders'
...     id = Column('id', Integer, primary_key=True)
...     user_id = Column('user_id', Integer, ForeignKey('users.id'), nullable=False)
...     quantity = Column('quantity', Integer, nullable=False)
...     def __str__(self):
...        return 'Quantity: %s' % self.quantity

>>> class User(Base):
...     __tablename__ = 'users'
...     id = Column('id', Integer, primary_key=True)
...     name = Column('name', Unicode(30))
...     orders = relation(Order, backref='user')
...     def __str__(self):
...         return self.name

>>> Base.metadata.create_all()
>>> session = Session()

>>> bill = User(name='Bill')
>>> john = User(name='John')
>>> order1 = Order(user=bill, quantity=10)
>>> session.commit()

}}}

Now, let's render a form for editing the order we've created:

{{{
>>> from formalchemy import FieldSet
>>> from formalchemy.regression import pretty_html # obviously unnecessary in production
>>> fs = FieldSet(order1)
>>> print pretty_html(fs.render())
<div>
 <label class="field_req" for="quantity">
  Quantity
 </label>
 <input id="quantity" name="quantity" type="text" value="10" />
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
  <option value="1" selected="selected">
   Bill
  </option>
  <option value="2">
   John
  </option>
 </select>
</div>

}}}

Note how the options for the User input are automatically loaded from the
database.

Now let's process some user input. In a real application, you'd get the post
data from your request object; here we'll just hardcode some:

{{{
>>> fs = FieldSet(order1, data={'quantity': 7, 'user_id': 2})
>>> if fs.validate():
...     fs.sync()

>>> order1.quantity
7
>>> order1.user_id
2
>>> session.commit()

}}}

=!FormAlchemy's current state=

!FormAlchemy is in alpha stage and the API is in constant
evolution. We think it's useful enough to release, but your code may
break from one version to another until !FormAlchemy 1.0 is released.
"""
