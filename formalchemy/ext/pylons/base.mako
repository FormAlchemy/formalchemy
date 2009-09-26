<%
from pylons import url, request
%>\
<html>
<head>
<title>${self.title()}</title>
<style media="screen" type="text/css"><!-- @import url(${url('static_contents', id='admin.css')}); --></style>
<style type="text/css">
.add {
    margin-left:1em;
    margin-bottom: 0.3em;
    background: url('${url('static_contents', id='add.png')}');
}
.delete {
    background: url('${url('static_contents', id='delete.png')}');
    float:left;
}
.edit {
    background: url('${url('static_contents', id='edit.png')}');
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
      <a href="${url('admin')}">
        ${F_('Home')}
      </a>
    %endif
    %if modelname and (id or request.path_info.endswith('/new')):
      <a href="${url('models', modelname=modelname)}">
        ${F_(modelname)} ${F_('listing')}
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
