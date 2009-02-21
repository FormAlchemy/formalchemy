# -*- coding: utf-8 -*-
import os
import sys

# put tempita on the path
sys.path.append(os.path.split(os.path.abspath(__file__))[0])

from formalchemy.i18n import get_translator
from formalchemy import helpers

from tempita import Template as TempitaTemplate
try:
    from mako.template import Template as MakoTemplate
    HAS_MAKO = True
except ImportError:
    HAS_MAKO = False
try:
    from genshi.template import GenshiTemplateLoader
    HAS_GENSHI = True
except ImportError:
    HAS_GENSHI = False

MAKO_TEMPLATES = os.path.join(
        os.path.dirname(__file__),
        'paster_templates','pylons_fa','+package+','templates')

class TemplateEngine(object):
    directories = []
    _templates = ['fieldset', 'fieldset_readonly',
                  'grid', 'grid_readonly']
    def __init__(self, **kw):
        self.templates = {}
        if 'directories' in kw:
            self.directories = list(kw.pop('directories'))
        for name in self._templates:
            self.templates[name] = self.get_template(name, **kw)

    def get_template(self, name, **kw):
        return None

    def render(self, template_name, **kwargs):
        return ''

    def __call__(self, template_name, **kw):
        if 'F_' not in kw:
            kw['F_'] = get_translator(kw.get('lang', None)).gettext
        if 'html' not in kw:
            kw['html'] = helpers
        return self.render(template_name, **kw)

class TempitaEngine(TemplateEngine):
    """Template engine for tempita
    """
    def get_template(self, name, **kw):
        for dirname in self.directories + [os.path.dirname(__file__)]:
            filename = os.path.join(dirname, '%s.tmpl' % name)
            if os.path.isfile(filename):
                return TempitaTemplate.from_filename(filename, **kw)

    def render(self, template_name, **kwargs):
        template = self.templates.get(template_name, None)
        return template.substitute(**kwargs)

class MakoEngine(TemplateEngine):
    """Template engine for mako
    """
    def get_template(self, name, **kw):
        for dirname in self.directories:
            filename = os.path.join(dirname, '%s.mako' % name)
            if os.path.isfile(filename):
                return MakoTemplate(filename=filename, **kw)
        filename = os.path.join(MAKO_TEMPLATES, '%s.mako_tmpl' % name)
        if os.path.isfile(filename):
            template = TempitaTemplate.from_filename(filename)
            return MakoTemplate(template.substitute(template_engine='mako'), **kw)

    def render(self, template_name, **kwargs):
        template = self.templates.get(template_name, None)
        return template.render_unicode(**kwargs)

class GenshiEngine(object):
    """Template engine for genshi
    """
    def get_template(self, name, **kw):
        for dirname in self.directories:
            filename = os.path.join(dirname, '%s.html' % name)
            if os.path.isfile(filename):
                loader = TemplateLoader(dirname, **kw)
                return loader.load('%s.html' % name)
        raise ValueError('%s.html not found in %s' % (name, ':'.join(self.directories)))

    def render(self, template_name, **kwargs):
        template = self.templates.get(template_name, None)
        return template.generate(**kwargs).render('html', doctype='html')


if HAS_MAKO:
    default_engine = MakoEngine(input_encoding='utf-8', output_encoding='utf-8')
    engines = dict(mako=default_engine, tempita=TempitaEngine())
else:
    default_engine = TempitaEngine()
    engines = dict(tempita=TempitaEngine())
