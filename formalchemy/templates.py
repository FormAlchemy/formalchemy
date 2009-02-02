# -*- coding: utf-8 -*-
from paste.script.templates import Template
from tempita import paste_script_template_renderer

class PylonsTemplate(Template):
    _template_dir = ('formalchemy', 'paster_templates/pylons_fa')
    summary = 'Pylons template with formalchemy support'
    required_templates = ['pylons']
    template_renderer = staticmethod(paste_script_template_renderer)

