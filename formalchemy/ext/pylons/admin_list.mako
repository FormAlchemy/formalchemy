<%inherit file="base.mako"/>\
<%!
from pylons import url
%>\
<%def name="title()">
${c.modelname}
</%def>

<%def name="sidebar()">
<div id="sidebar">
<div class="box">
<h2>${F_('Related types')}</h2>
  <table>
  %for field in c.grid._fields.itervalues():
    %if field.is_relation:
      <% clsname = field.relation_type().__name__ %>
      <tr><td><a href="${url(controller=controller, modelname=clsname, action='list')}">${clsname}</a></td></tr>
    %endif
  %endfor
  </table>
</div>
</div>
</%def>

<div class="box">
<h2>
${F_('Existing objects')}
</h2>
<div id="pager">
${page.pager()}
</div>
<table>
  ${c.grid.render()}
</table>
<a class="icon add" title="${F_('New object')}" href="${url(controller=controller, modelname=c.modelname, action='edit')}">
${F_('New object')}
</a>
</div>
