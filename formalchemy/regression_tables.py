from regression import *

__doc__ = """
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
"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()
