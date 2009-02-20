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

