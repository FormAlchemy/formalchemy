<%
from pylons import url
%>\
<html>
<head>
<title>${self.title()}</title>
<style media="screen" type="text/css"><!-- @import url(${url(controller=controller, modelname='static_contents', action='admin.css')}); --></style>
<style type="text/css">
.add {
    margin-left:1em;
    margin-bottom: 0.3em;
    background: url('${url(controller=controller, modelname='static_contents', action='add.png')}');
}
.delete {
    background: url('${url(controller=controller, modelname='static_contents', action='delete.png')}');
    float:left;
}
.edit {
    background: url('${url(controller=controller, modelname='static_contents', action='edit.png')}');
    float:left;
}
</style>
${custom_css}
${custom_js}
</head>
<body>
<div id="header">
    <div id="title"><h1>${self.title()}</h1></div>
    <div id="nav">
    %if modelname:
      <a href="${url(controller=controller)}">
        ${F_('Models')}
      </a>
    %endif
    </div>
</div>

<%def name="sidebar()">
</%def>
${self.sidebar()}

<div id="content">
<%
from pylons import session
flashes = session.get('_admin_flashes', [])
if flashes:
   session['_admin_flashes'] = []
   session.save()
%>
%for flash in flashes:
  <div class='admin-flash'>${flash}</div>
%endfor
${self.body()}
</div>
<div id="footer">
</div>
</body>
</html>
