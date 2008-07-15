from regression import *
from tables import *

__doc__ = """
>>> t = Table(bill)
>>> print pretty_html(t.render())
<tbody>
 <tr>
  <td class="table_label">
   Email:
  </td>
  <td class="table_field">
   bill@example.com
  </td>
 </tr>
 <tr>
  <td class="table_label">
   Password:
  </td>
  <td class="table_field">
   1234
  </td>
 </tr>
 <tr>
  <td class="table_label">
   Name:
  </td>
  <td class="table_field">
   Bill
  </td>
 </tr>
 <tr>
  <td class="table_label">
   Orders:
  </td>
  <td class="table_field">
   Quantity: 10
  </td>
 </tr>
</tbody>

>>> t = TableCollection(User, [bill])
>>> print pretty_html(t.render())
<thead>
 <tr>
  <th>
   Email:
  </th>
  <th>
   Password:
  </th>
  <th>
   Name:
  </th>
  <th>
   Orders:
  </th>
 </tr>
</thead>
<tbody>
 <tr>
  <td>
   bill@example.com
  </td>
  <td>
   1234
  </td>
  <td>
   Bill
  </td>
  <td>
   Quantity: 10
  </td>
 </tr>
</tbody>

>>> t = TableCollection(User, [bill, john])
>>> t.add(Field('link', type=types.String, value=lambda item: '<a href=%d>link</a>' % item.id))
>>> print pretty_html(t.render())
<thead>
 <tr>
  <th>
   Email:
  </th>
  <th>
   Password:
  </th>
  <th>
   Name:
  </th>
  <th>
   Orders:
  </th>
  <th>
   Link:
  </th>
 </tr>
</thead>
<tbody>
 <tr>
  <td>
   bill@example.com
  </td>
  <td>
   1234
  </td>
  <td>
   Bill
  </td>
  <td>
   Quantity: 10
  </td>
  <td>
   <a href="1">
    link
   </a>
  </td>
 </tr>
 <tr>
  <td>
   john@example.com
  </td>
  <td>
   5678
  </td>
  <td>
   John
  </td>
  <td>
   Quantity: 5
  </td>
  <td>
   <a href="2">
    link
   </a>
  </td>
 </tr>
</tbody>

>>> g = Grid(User, [bill, john])
>>> print pretty_html(g.render())
"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()
