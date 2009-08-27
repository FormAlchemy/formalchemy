# -*- coding: utf-8 -*-
from setuptools import setup
import xml.sax.saxutils
import os

def read(filename):
    text = open(filename).read()
    text = unicode(text, 'utf-8').encode('ascii', 'xmlcharrefreplace')
    return xml.sax.saxutils.escape(text)

long_description = '.. contents::\n\n' +\
                   'Description\n' +\
                   '===========\n\n' +\
                   read('README.txt') +\
                   '\n\n' +\
                   'Changes\n' +\
                   '=======\n\n' +\
                   read('CHANGELOG.txt')

setup(name='FormAlchemy',
      license='MIT License',
      version='1.2.1',
      description='FormAlchemy greatly speeds development with SQLAlchemy mapped classes (models) in a HTML forms environment.',
      long_description=long_description,
      author='Alexandre Conrad, Jonathan Ellis, Gaël Pasgrimaud',
      author_email='formalchemy@googlegroups.com',
      url='http://formalchemy.googlecode.com',
      download_url='http://code.google.com/p/formalchemy/downloads/list',
      install_requires=['SQLAlchemy', 'Tempita'],
      packages=['formalchemy',
                'formalchemy.ext', 'formalchemy.ext.pylons'],
      package_data={'formalchemy': ['*.tmpl', 'i18n_resources/*/LC_MESSAGES/formalchemy.mo',
                                    'ext/pylons/*.mako', 'ext/pylons/*.css', 'ext/pylons/*.png',
                                    'tests/data/mako/*.mako', 'tests/data/genshi/*.html',
                                    'paster_templates/pylons_fa/+package+/*/*_tmpl',
                                    ]},
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Software Development :: User Interfaces',
          'Topic :: Text Processing :: Markup :: HTML',
          'Topic :: Utilities',
      ],
      message_extractors = {'formalchemy': [
              ('**.py', 'python', None),
              ('**.mako', 'mako', None),
              ('**.tmpl', 'python', None)]},
      zip_safe=False,
      entry_points = """
      [paste.paster_create_template]
      pylons_fa = formalchemy.ext.pylons.pastertemplate:PylonsTemplate
      """,
      )

