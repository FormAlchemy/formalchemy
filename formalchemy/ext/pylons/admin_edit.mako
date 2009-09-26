<%inherit file="base.mako"/>\
<%
from pylons import url
%>\
<%def name="title()">
${F_(action)} ${modelname} ${id and id or ''}
</%def>
<fieldset>
<legend>
${F_(action)} ${modelname} ${id and id or ''}
</legend>
<form method="POST" action="${id and url('view_model', modelname=modelname, id=id) or url('models', modelname=modelname)}">
  ${c.fs.render()}
  <div class="form_controls">
      %if id:
        <input type="hidden" name="_method" value="PUT" />
      %else:
        <input type="hidden" name="_method" value="POST" />
      %endif
      <input type="submit" class="button">
      <input type="button" value="${F_('Cancel')}" class="button"
             onclick="javascript:window.location = '${url("models", modelname=modelname)}'" />
  </div>
</form>
</fieldset>
