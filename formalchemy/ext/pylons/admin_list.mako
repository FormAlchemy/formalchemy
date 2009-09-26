<%inherit file="base.mako"/>\
<%!
from pylons import url
%>\
<%def name="title()">
${modelname}
</%def>

<%def name="sidebar()">
%if clsnames:
<div id="sidebar">
<div class="box">
<h2>${F_('Related types')}</h2>
  <table>
  %for clsname in clsnames:
    <tr><td><a href="${url('models', modelname=clsname)}">${clsname}</a></td></tr>
  %endfor
  </table>
</div>
</div>
%endif
</%def>

<div class="box">
<h2>
${F_('Existing objects')}
</h2>
<div id="pager">
${page.pager()}
</div>
<table>
  ${grid.render()}
</table>
<a class="icon add" title="${F_('New object')}" href="${url('new_model', modelname=c.modelname)}">
${F_('New object')}
</a>
</div>
