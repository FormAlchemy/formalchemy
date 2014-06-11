<ul>
%for field in fieldset.render_fields.values():
<li>${field.name}</li>
%endfor
</ul>
