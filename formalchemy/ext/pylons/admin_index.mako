<%inherit file="base.mako"/>\
<%
from pylons.controllers.util import url_for
%>\
<%def name="title()">
${F_('Models')}
</%def>
<table>
%for i, modelname in enumerate(modelnames):
  <tr class="${i % 2 and 'odd' or 'even'}"><td><a href="${url_for(controller=controller, modelname=modelname, action='list')}">${modelname}</a></td></tr>
%endfor
</table>
