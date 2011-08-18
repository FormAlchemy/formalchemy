# -*- coding: utf-8 -*-
import os
import sys

from formalchemy.i18n import get_translator
from formalchemy import helpers

from tempita import Template as TempitaTemplate
try:
    from mako.lookup import TemplateLookup
    from mako.template import Template as MakoTemplate
    from mako.exceptions import TopLevelLookupException
    HAS_MAKO = True
except ImportError:
    HAS_MAKO = False
try:
    from genshi.template import TemplateLoader as GenshiTemplateLoader
    HAS_GENSHI = True
except ImportError:
    HAS_GENSHI = False

MAKO_TEMPLATES = os.path.join(
        os.path.dirname(__file__),
        'paster_templates','pylons_fa','+package+','templates', 'forms')

class TemplateEngine(object):
    """Base class for templates engines
    """
    directories = []
    extension = None
    _templates = ['fieldset', 'fieldset_readonly',
                  'grid', 'grid_readonly']
    def __init__(self, **kw):
        self.templates = {}
        if 'extension' in kw:
            self.extension = kw.pop('extension')
        if 'directories' in kw:
            self.directories = list(kw.pop('directories'))
        for name in self._templates:
            self.templates[name] = self.get_template(name, **kw)

    def get_template(self, name, **kw):
        """return the template object for `name`. Must be override by engines"""
        return None

    def get_filename(self, name):
        """return the filename for template `name`"""
        for dirname in self.directories + [os.path.dirname(__file__)]:
            filename = os.path.join(dirname, '%s.%s' % (name, self.extension))
            if os.path.isfile(filename):
                return filename

    def render(self, template_name, **kwargs):
        """render the template. Must be override by engines"""
        return ''

    def _update_args(cls, kw):
        kw['F_'] = get_translator(lang=kw.get('lang', None),
                                  request=kw.get('request', None))
        kw['html'] = helpers
        return kw
    _update_args = classmethod(_update_args)

    def __call__(self, template_name, **kw):
        """update kw to extend the namespace with some FA's utils then call `render`"""
        self._update_args(kw)
        return self.render(template_name, **kw)

class TempitaEngine(TemplateEngine):
    """Template engine for tempita. File extension is `.tmpl`.
    """
    extension = 'tmpl'
    def get_template(self, name, **kw):
        filename = self.get_filename(name)
        if filename:
            return TempitaTemplate.from_filename(filename, **kw)

    def render(self, template_name, **kwargs):
        template = self.templates.get(template_name, None)
        return template.substitute(**kwargs)

class MakoEngine(TemplateEngine):
    """Template engine for mako. File extension is `.mako`.
    """
    extension = 'mako'
    _lookup = None
    def get_template(self, name, **kw):
        if self._lookup is None:
            self._lookup = TemplateLookup(directories=self.directories, **kw)
        try:
            return self._lookup.get_template('%s.%s' % (name, self.extension))
        except TopLevelLookupException:
            filename = os.path.join(MAKO_TEMPLATES, '%s.mako_tmpl' % name)
            if os.path.isfile(filename):
                template = TempitaTemplate.from_filename(filename)
                return MakoTemplate(template.substitute(template_engine='mako'), **kw)

    def render(self, template_name, **kwargs):
        template = self.templates.get(template_name, None)
        return template.render_unicode(**kwargs)

class GenshiEngine(TemplateEngine):
    """Template engine for genshi. File extension is `.html`.
    """
    extension = 'html'
    def get_template(self, name, **kw):
        filename = self.get_filename(name)
        if filename:
            loader = GenshiTemplateLoader(os.path.dirname(filename), **kw)
            return loader.load(os.path.basename(filename))

    def render(self, template_name, **kwargs):
        template = self.templates.get(template_name, None)
        return template.generate(**kwargs).render('html', doctype=None)


if HAS_MAKO:
    default_engine = MakoEngine(input_encoding='utf-8', output_encoding='utf-8')
    engines = dict(mako=default_engine, tempita=TempitaEngine())
else:
    default_engine = TempitaEngine()
    engines = dict(tempita=TempitaEngine())
