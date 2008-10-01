__doc__ = r"""
>>> from formalchemy.tests import *
>>> from formalchemy import Grid

>>> g = Grid(User)
>>> g.rebind([bill, john]) # explicitly test rebind
>>> print pretty_html(g.render())
<thead>
 <tr>
  <th>
   Email
  </th>
  <th>
   Password
  </th>
  <th>
   Name
  </th>
  <th>
   Orders
  </th>
 </tr>
</thead>
<tbody>
 <tr>
  <td>
   <input id="User-1-email" maxlength="40" name="User-1-email" type="text" value="bill@example.com" />
  </td>
  <td>
   <input id="User-1-password" maxlength="20" name="User-1-password" type="text" value="1234" />
  </td>
  <td>
   <input id="User-1-name" maxlength="30" name="User-1-name" type="text" value="Bill" />
  </td>
  <td>
   <select id="User-1-orders" multiple="multiple" name="User-1-orders" size="5">
    <option value="1" selected="selected">
     Quantity: 10
    </option>
    <option value="2">
     Quantity: 5
    </option>
    <option value="3">
     Quantity: 6
    </option>
   </select>
  </td>
 </tr>
 <tr>
  <td>
   <input id="User-2-email" maxlength="40" name="User-2-email" type="text" value="john@example.com" />
  </td>
  <td>
   <input id="User-2-password" maxlength="20" name="User-2-password" type="text" value="5678" />
  </td>
  <td>
   <input id="User-2-name" maxlength="30" name="User-2-name" type="text" value="John" />
  </td>
  <td>
   <select id="User-2-orders" multiple="multiple" name="User-2-orders" size="5">
    <option value="1">
     Quantity: 10
    </option>
    <option value="2" selected="selected">
     Quantity: 5
    </option>
    <option value="3" selected="selected">
     Quantity: 6
    </option>
   </select>
  </td>
 </tr>
</tbody>

>>> g = Grid(User, [john, bill])
>>> g.rebind(data={'User-1-email': '', 'User-1-password': '1234_', 'User-1-name': 'Bill_', 'User-1-orders': '1', 'User-2-email': 'john_@example.com', 'User-2-password': '5678_', 'User-2-name': 'John_', 'User-2-orders': ['2', '3'], })
>>> g.validate()
False
>>> g.errors[bill]
{AttributeField(email): ['Please enter a value']}
>>> g.errors[john]
{}
>>> g.sync_one(john)
>>> session.flush()
>>> session.refresh(john)
>>> john.email == 'john_@example.com'
True

>>> session.rollback()

Test preventing user from binding to the wrong kind of object:
>>> g = g.bind([john])
>>> g.rows == [john]
True
>>> g.rebind(User)
Traceback (most recent call last):
...
Exception: instances must be an iterable, not <class 'formalchemy.tests.User'>
>>> g = g.bind(User)
Traceback (most recent call last):
...
Exception: instances must be an iterable, not <class 'formalchemy.tests.User'>

Simulate creating a grid in a different thread than it's used in:
>>> _Session = sessionmaker(bind=engine)
>>> _old_session = _Session()
>>> assert _old_session != object_session(john)
>>> g = Grid(User, session=_old_session)
>>> g2 = g.bind([john])
>>> _ = g2.render()
"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()
