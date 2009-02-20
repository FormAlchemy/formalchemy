# -*- coding: utf-8 -*-
<thead>
  <tr>
    %for field in collection.render_fields.itervalues():
      <th>${F_(field.label_text or collection.prettify(field.key))|h}</th>
    %endfor
  </tr>
</thead>

<tbody>
%for i, row in enumerate(collection.rows):
  <% collection._set_active(row) %>
  <tr class="${i % 2 and 'odd' or 'even'}">
  %for field in collection.render_fields.itervalues():
    <td>${field.render_readonly()|n}</td>
  %endfor
  </tr>
%endfor
</tbody>
