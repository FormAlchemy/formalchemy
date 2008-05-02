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
  ${h.content_tag("label", content=attr.label_text or prettify(attr.key), for_=attr.name, class_=attr.nullable and 'field_opt' or 'field_req')}
  ${attr.render()}
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
    
    def render(self, prettify=base.prettify, focus=True):
        return template.render(attrs=self.render_attrs, fields=fields, h=h, prettify=prettify, focus=focus)
