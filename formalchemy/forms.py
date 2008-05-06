# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import logging
logger = logging.getLogger('formalchemy.' + __name__)

import helpers as h
import base, fields, utils
from validators import ValidationException
from mako.template import Template

__all__ = ["AbstractFieldSet, FieldSet"]


class AbstractFieldSet(base.ModelRender):
    """
    The `FieldSet` class.

    This class is responsible for generating HTML fields from a given
    `model`.

    The one method to use is `render`. This is the method that returns
    generated HTML code from the `model` object.
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
        errors.update([(attr, attr.errors) for attr in self.render_attrs if attr.errors])
        return errors


template_text = """
<% _focus_rendered = False %>
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

class FieldSet(AbstractFieldSet):
    """
    Default FieldSet implementation.  Adds prettify, focus options.
    """
    def __init__(self, *args, **kwargs):
        AbstractFieldSet.__init__(self, *args, **kwargs)
        self.prettify = base.prettify
        self.focus = True

    def configure(self, pk=False, exclude=[], include=[], options=[], global_validator=None, prettify=base.prettify, focus=True):
        AbstractFieldSet.configure(self, pk, exclude, include, options, global_validator)
        self.prettify = prettify
        self.focus = focus

    def render(self):
        """default template understands extra args 'prettify' and 'focus'"""
        return template.render(attrs=self.render_attrs, global_errors=self._errors, fields=fields, h=h, prettify=self.prettify, focus=self.focus)
