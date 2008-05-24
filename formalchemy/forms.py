# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import logging
logger = logging.getLogger('formalchemy.' + __name__)

import helpers as h
import base, fields, utils
from validators import ValidationException
from tempita import Template

__all__ = ['form_data', 'AbstractFieldSet', 'FieldSet']


def form_data(form, post):
    """ 
    Given POST data (currently must be an object providing getone and
    getall, like paste's MultiDict), transform it into data suitable for use
    in bind(). 
    
    getone and getall are described at
    http://pythonpaste.org/module-paste.util.multidict.html
    """
    if not (hasattr(post, 'getall') and hasattr(post, 'getone')):
        raise Exception('unsupported post object.  see help(formdata) for supported interfaces')
    d = {}
    for attr in form.render_attrs:
        if attr.is_collection():
            d[attr.name] = post.getall(attr.name)
        else:
            d[attr.name] = post.getone(attr.name)
    return d

class AbstractFieldSet(base.ModelRender):
    """
    `FieldSets` are responsible for generating HTML fields from a given
    `model`.

    The one method you must implement is `render`. This is the method that returns
    generated HTML code from the `model` object.  See `FieldSet` for the default
    implementation.
    """
    def __init__(self, *args, **kwargs):
        base.ModelRender.__init__(self, *args, **kwargs)
        self.validator = None
        self._errors = []

    def configure(self, pk=False, exclude=[], include=[], options=[], global_validator=None):
        base.ModelRender.configure(self, pk, exclude, include, options)
        self.validator = global_validator

    def validate(self):
        if self.data is None:
            raise Exception('Cannot validate without binding data')
        success = True
        for attr in self.render_attrs:
            success = attr._validate() and success
        if self.validator:
            try:
                self.validator(self.data)
            except ValidationException, e:
                self._errors = e.args
                success = False
        return success
    
    def errors(self):
        errors = {}
        if self._errors:
            errors[None] = self._errors
        errors.update(dict([(attr, attr.errors)
                            for attr in self.render_attrs if attr.errors]))
        return errors
    
    
template_text_mako = r"""
<% _focus_rendered = False %>\

% for error in global_errors:
<div class="fieldset_error">
  ${error}
</div>
% endfor

% for attr in attrs:
  % if attr.render_as == fields.HiddenField:
${attr.render()}
  % else:
<div>
  <label class="${attr.is_required() and 'field_req' or 'field_opt'}" for="${attr.name}">${attr.label_text or prettify(attr.key)}</label>
  ${attr.render()}
  % for error in attr.errors:
  <span class="field_error">${error}</span>
  % endfor
</div>

% if (focus == attr or focus is True) and not _focus_rendered:
<script type="text/javascript">
//<![CDATA[
document.getElementById("${attr.name}").focus();
//]]>
</script>
<% _focus_rendered = True %>\
% endif

% endif
% endfor
""".strip()

template_text_tempita = r"""
{{py:_focus_rendered = False}}

{{for error in global_errors}}
<div class="fieldset_error">
  {{error}}
</div>
{{endfor}}

{{for attr in attrs}}                                                                          
{{if attr.render_as == fields.HiddenField}}                                                    
{{attr.render()}}                                                                              
{{else}}                                                                                       
<div>                                                                                          
  <label class="{{attr.is_required() and 'field_req' or 'field_opt'}}" for="{{attr.name}}">{{attr.label_text or prettify(attr.key)}}</label>
  {{attr.render()}}                                                                            
  {{for error in attr.errors}}
  <span class="field_error">{{error}}</span>
  {{endfor}}
</div>                                                                                         

{{if (focus == attr or focus is True) and not _focus_rendered}}
<script type="text/javascript">
//<![CDATA[
document.getElementById("{{attr.name}}").focus();
//]]>
</script>
{{py:_focus_rendered = True}}
{{endif}}

{{endif}}                                                                                      
{{endfor}}                                                                                     
""".strip()
template_tempita = Template(template_text_tempita, name='fieldset_template')
render_tempita = template_tempita.substitute

try:
    from mako.template import Template as MakoTemplate
except ImportError:
    render = render_tempita
else:
    template_mako = MakoTemplate(template_text_mako)
    render = render_mako = template_mako.render

# todo use mako template as default; fall back to tempita if import fails?
# how do we test this nicely?

class FieldSet(AbstractFieldSet):
    """
    Default FieldSet implementation.  Adds prettify, focus options.
    
    You can override the default prettify either by subclassing:
    
    class MyFieldSet(FieldSet):
        prettify = staticmethod(myprettify)
        
    or just on a per-instance basis:
    
    fs = FieldSet(...)
    fs.prettify = myprettify
    """
    prettify = staticmethod(base.prettify)
    
    def __init__(self, *args, **kwargs):
        AbstractFieldSet.__init__(self, *args, **kwargs)
        self.focus = True

    def configure(self, pk=False, exclude=[], include=[], options=[], global_validator=None, focus=True):
        """default template understands extra args 'prettify' and 'focus'"""
        AbstractFieldSet.configure(self, pk, exclude, include, options, global_validator)
        self.focus = focus

    def render(self):
        # we pass 'fields' because a relative import in the template
        # won't work in production, and an absolute import makes testing more of a pain.
        # since the FA test suite won't concern you if you roll your own FieldSet,
        # feel free to perform such imports in the template.
        return render(attrs=self.render_attrs, global_errors=self._errors, fields=fields, prettify=self.prettify, focus=self.focus)
