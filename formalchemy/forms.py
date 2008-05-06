# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import logging
logger = logging.getLogger('formalchemy.' + __name__)

import helpers as h
import base, fields, utils
from mako.template import Template

__all__ = ["FieldSet"]


template_text = """
<% _focus_rendered = False %>
% for attr in attrs:
  % if attr.render_as == fields.HiddenField:
${attr.render()}
  % else:
<div>
  ${h.content_tag("label", content=attr.label_text or prettify(attr.key), for_=attr.name, class_=attr.is_required() and 'field_req' or 'field_opt')}
  ${attr.render()}
  % for error in attr.errors:
  <span class="field_error">${error}</span>
  % endfor
</div>
% if (focus == attr or focus is True) and not _focus_rendered:
${h.javascript_tag('document.getElementById("%s").focus();' % attr.name)}
<% _focus_rendered = True %>
% endif
% endif
% endfor
""".strip()
template = Template(template_text)

class FieldSet(base.ModelRender):
    """The `FieldSet` class.

    This class is responsible for generating HTML fields from a given
    `model`.

    The one method to use is `render`. This is the method that returns
    generated HTML code from the `model` object.
    """
    
    def render(self):
        """default template understands extra args 'prettify' and 'focus'"""
        prettify = self.render_opts.get('prettify', base.prettify)
        focus = self.render_opts.get('focus', True)
        return template.render(attrs=self.render_attrs, fields=fields, h=h, prettify=prettify, focus=focus)

    def validate(self):
        if self.data is None:
            raise Exception('Cannot validate without binding data')
        success = True
        for attr in self.render_attrs:
            success = attr._validate() and success
        return success
    
    def errors(self):
        errors = {}
        errors.update([(attr, attr.errors) for attr in self.render_attrs if attr.errors])
        return errors

    def sync(self):
        for attr in self.render_attrs:
            attr.sync()
