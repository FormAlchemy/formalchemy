<%inherit file="base.mako"/>\
<%
from pylons.controllers.util import url_for
%>\
<%def name="title()">
${F_(action)} ${modelname} ${id and id or ''}
</%def>
<fieldset>
<legend>
${F_(action)} ${modelname} ${id and id or ''}
</legend>
<form method="post">
  ${c.fs.render()}
  <div class="form_controls">
      <input type="submit" class="button">
      <input type="button" value="${F_('Cancel')}" class="button"
             onclick="javascript:window.location = '${url_for(controller=controller, modelname=modelname, action='list', id=None)}'" />
  </div>
</form>
</fieldset>
