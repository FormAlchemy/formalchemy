from formalchemy.tests import *
def test_rebind_and_render(self):
    """Explicitly test rebind + render:

    >>> g = Grid(User, session=session)
    >>> g.rebind([bill, john])
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
     <tr class="even">
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
        <option value="2">
         Quantity: 5
        </option>
        <option value="3">
         Quantity: 6
        </option>
        <option selected="selected" value="1">
         Quantity: 10
        </option>
       </select>
      </td>
     </tr>
     <tr class="odd">
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
        <option selected="selected" value="2">
         Quantity: 5
        </option>
        <option selected="selected" value="3">
         Quantity: 6
        </option>
        <option value="1">
         Quantity: 10
        </option>
       </select>
      </td>
     </tr>
    </tbody>
    """

def test_extra_field():
    """
    Test rendering extra field:
    >>> g = Grid(User, session=session)
    >>> g.add(Field('edit', types.String, 'fake edit link'))
    >>> g._set_active(john)
    >>> print g.edit.render()
    <input id="User-2-edit" name="User-2-edit" type="text" value="fake edit link" />

    And extra field w/ callable value:
    >>> g = Grid(User, session=session)
    >>> g.add(Field('edit', types.String, lambda o: 'fake edit link for %s' % o.id))
    >>> g._set_active(john)
    >>> print g.edit.render()
    <input id="User-2-edit" name="User-2-edit" type="text" value="fake edit link for 2" />

    Text syncing:
    >>> g = Grid(User, [john, bill], session=session)
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

def test_rebind_render():
    """
    Explicitly test rebind + render:
    >>> g = Grid(User, session=session, prefix="myprefix")
    >>> g.rebind([bill, john])
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
     <tr class="even">
      <td>
       <input id="myprefix-User-1-email" maxlength="40" name="myprefix-User-1-email" type="text" value="bill@example.com" />
      </td>
      <td>
       <input id="myprefix-User-1-password" maxlength="20" name="myprefix-User-1-password" type="text" value="1234" />
      </td>
      <td>
       <input id="myprefix-User-1-name" maxlength="30" name="myprefix-User-1-name" type="text" value="Bill" />
      </td>
      <td>
       <select id="myprefix-User-1-orders" multiple="multiple" name="myprefix-User-1-orders" size="5">
        <option value="2">
         Quantity: 5
        </option>
        <option value="3">
         Quantity: 6
        </option>
        <option selected="selected" value="1">
         Quantity: 10
        </option>
       </select>
      </td>
     </tr>
     <tr class="odd">
      <td>
       <input id="myprefix-User-2-email" maxlength="40" name="myprefix-User-2-email" type="text" value="john@example.com" />
      </td>
      <td>
       <input id="myprefix-User-2-password" maxlength="20" name="myprefix-User-2-password" type="text" value="5678" />
      </td>
      <td>
       <input id="myprefix-User-2-name" maxlength="30" name="myprefix-User-2-name" type="text" value="John" />
      </td>
      <td>
       <select id="myprefix-User-2-orders" multiple="multiple" name="myprefix-User-2-orders" size="5">
        <option selected="selected" value="2">
         Quantity: 5
        </option>
        <option selected="selected" value="3">
         Quantity: 6
        </option>
        <option value="1">
         Quantity: 10
        </option>
       </select>
      </td>
     </tr>
    </tbody>
    >>> g.rebind(data={'myprefix-User-1-email': 'updatebill_@example.com', 'myprefix-User-1-password': '1234_', 'myprefix-User-1-name': 'Bill_', 'myprefix-User-1-orders': '1', 'myprefix-User-2-email': 'john_@example.com', 'myprefix-User-2-password': '5678_', 'myprefix-User-2-name': 'John_', 'myprefix-User-2-orders': ['2', '3'], })
    >>> g.validate()
    True
    >>> g.sync()
    >>> bill.email
    u'updatebill_@example.com'
    """

if __name__ == '__main__':
    import doctest
    doctest.testmod()
