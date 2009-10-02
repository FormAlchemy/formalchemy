{{if template_engine == 'mako'}}
# -*- coding: utf-8 -*-
<tbody>
%for field in fieldset.render_fields.itervalues():
  <tr>
    <td class="field_readonly">${[field.label_text, fieldset.prettify(field.key)][int(field.label_text is None)]|h}:</td>
    <td>${field.render_readonly()|n}</td>
  </tr>
%endfor
</tbody>
{{endif}}
