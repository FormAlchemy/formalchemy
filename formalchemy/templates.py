# -*- coding: utf-8 -*-
import os
import sys

# put tempita on the path
sys.path.append(os.path.split(os.path.abspath(__file__))[0])

from tempita import Template as TempitaTemplate
try:
    from mako.template import Template as MakoTemplate
    HAS_MAKO = True
except ImportError:
    HAS_MAKO = False

TEMPLATES_DIR = os.path.join(
        os.path.dirname(__file__),
        'paster_templates','pylons_fa','+package+','templates')

class TemplateEngine(object):
    directories = []
    _templates = dict(
            fieldset=None,
            fieldset_readonly=None,
            grid=None,
            grid_readonly=None)
    def __init__(self, **kw):
        self.templates = {}
        if 'directories' in kw:
            self.directories = kw.pop('directories')
        for name in self._templates:
            self.templates[name] = self.get_template(name)

    def render(self, template_name, **kwargs):
        return NotImplementedError()

class TempitaEngine(TemplateEngine):
    _templates = dict(
    fieldset_readonly = r"""
{{py:import formalchemy.helpers as h}}
<tbody>
{{for field in fieldset.render_fields.itervalues()}}
  <tr>
    <td class="field_readonly">{{h.escape_once([field.label_text, fieldset.prettify(field.key)][int(field.label_text is None)])}}:</td>
    <td>{{field.render_readonly()}}</td>
  </tr>
{{endfor}}
</tbody>
""",
    fieldset = r"""
{{py:import formalchemy.helpers as h}}
{{py:_focus_rendered = False}}
{{py:_ = F_}}

{{for error in fieldset.errors.get(None, [])}}
<div class="fieldset_error">
  {{_(error)}}
</div>
{{endfor}}

{{for field in fieldset.render_fields.itervalues()}}
{{if field.requires_label}}
<div>
  <label class="{{field.is_required() and 'field_req' or 'field_opt'}}" for="{{field.renderer.name}}">{{h.escape_once([field.label_text, fieldset.prettify(field.key)][int(field.label_text is None)])}}</label>
  {{field.render()}}
  {{for error in field.errors}}
  <span class="field_error">{{_(error)}}</span>
  {{endfor}}
</div>

{{if (fieldset.focus == field or fieldset.focus is True) and not _focus_rendered}}
{{if not field.is_readonly()}}
<script type="text/javascript">
//<![CDATA[
document.getElementById("{{field.renderer.name}}").focus();
//]]>
</script>
{{py:_focus_rendered = True}}
{{endif}}
{{endif}}
{{else}}
{{field.render()}}
{{endif}}
{{endfor}}
""",
    grid_readonly = r"""
{{py:import formalchemy.helpers as h}}
<thead>
  <tr>
    {{for field in collection.render_fields.itervalues()}}
      <th>{{h.escape_once(F_(field.label_text or collection.prettify(field.key)))}}</th>
    {{endfor}}
  </tr>
</thead>

<tbody>
{{for i, row in enumerate(collection.rows):}}
  {{collection._set_active(row)}}
  <tr class="{{i % 2 and 'odd' or 'even'}}">
  {{for field in collection.render_fields.itervalues()}}
    <td>{{field.render_readonly()}}</td>
  {{endfor}}
  </tr>
{{endfor}}
</tbody>
""",
    grid = r"""
{{py:import formalchemy.helpers as h}}
<thead>
  <tr>
    {{for field in collection.render_fields.itervalues()}}
      <th>{{h.escape_once(F_(field.label_text or collection.prettify(field.key)))}}</td>
    {{endfor}}
  </tr>
</thead>

<tbody>
{{for i, row in enumerate(collection.rows):}}
  {{collection._set_active(row)}}
  <tr class="{{i % 2 and 'odd' or 'even'}}">
  {{for field in collection.render_fields.itervalues()}}
    <td>
      {{field.render()}}
      {{for error in field.errors}}
      <span class="grid_error">{{error}}</span>
      {{endfor}}
    </td>
  {{endfor}}
  </tr>
{{endfor}}
</tbody>
""",
    )

    def get_template(self, name, **kw):
        for dirname in self.directories:
            filename = os.path.join(dirname, '%s.tmpl' % name)
            if os.path.isfile(filename):
                return TempitaTemplate.from_filename(filename, **kw)
        return TempitaTemplate(self._templates[name])

    def render(self, template_name, **kwargs):
        template = self.templates.get(template_name, None)
        return template.substitute(**kwargs)

class MakoEngine(TemplateEngine):

    def get_template(self, name, **kw):
        for dirname in self.directories:
            filename = os.path.join(dirname, '%s.mako' % name)
            if os.path.isfile(filename):
                return MakoTemplate(filename=filename, **kw)
        filename = os.path.join(TEMPLATES_DIR, '%s.mako_tmpl' % name)
        if os.path.isfile(filename):
            template = TempitaTemplate.from_filename(filename)
            return MakoTemplate(template.substitute(template_engine='mako'), **kw)

    def render(self, template_name, **kwargs):
        template = self.templates.get(template_name, None)
        return template.render_unicode(**kwargs)

if HAS_MAKO:
    default_engine = MakoEngine(input_encoding='utf-8', output_encoding='utf-8')
    engines = dict(mako=default_engine, tempita=TempitaEngine())
else:
    default_engine = TempitaEngine()
    engines = dict(tempita=TempitaEngine())
