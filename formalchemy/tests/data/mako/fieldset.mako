<ul>
%for field in fieldset.render_fields.itervalues():
<li>${field.name}</li>
%endfor
</ul>
