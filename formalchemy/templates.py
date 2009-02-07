# -*- coding: utf-8 -*-
import os
from tempita import Template as TempitaTemplate

TEMPLATES_DIR = os.path.join(
        os.path.dirname(__file__),
        'paster_templates','pylons_fa','+package+','templates')

def mako_template(name):
    template = TempitaTemplate.from_filename(
                    os.path.join(TEMPLATES_DIR, '%s.mako_tmpl' % name))
    return template.substitute(template_engine='mako')

try:
    from tempita import paste_script_template_renderer
    from paste.script.templates import Template, var
except ImportError:
    class PylonsTemplate(object):
        pass
else:
    class PylonsTemplate(Template):
        _template_dir = ('formalchemy', 'paster_templates/pylons_fa')
        summary = 'Pylons application template with formalchemy support'
        required_templates = ['pylons']
        template_renderer = staticmethod(paste_script_template_renderer)
        vars = [
            var('admin_controller', 'Add formalchemy\'s admin controller',
                default=False),
            ]
