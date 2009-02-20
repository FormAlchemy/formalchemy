# -*- coding: utf-8 -*-
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

