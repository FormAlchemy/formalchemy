# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import xml.sax.saxutils
from os.path import join
import sys
import os

try:
    from msgfmt import Msgfmt
except:
    sys.path.insert(0, join(os.getcwd(), 'formalchemy'))
    from msgfmt import Msgfmt

def compile_po(path):
    for language in os.listdir(path):
        lc_path = join(path, language, 'LC_MESSAGES')
        if os.path.isdir(lc_path):
            for domain_file in os.listdir(lc_path):
                if domain_file.endswith('.po'):
                    file_path = join(lc_path, domain_file)
                    mo_file = join(lc_path, '%s.mo' % domain_file[:-3])
                    mo_content = Msgfmt(file_path, name=file_path).get()
                    mo = open(mo_file, 'wb')
                    mo.write(mo_content)
                    mo.close()

try:
    compile_po(join(os.getcwd(), 'formalchemy', 'i18n_resources'))
except Exception, e:
    print 'Error while building .mo files'
    print '%r - %s' % (e, e)

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
      version='1.3.4',
      description='FormAlchemy greatly speeds development with SQLAlchemy mapped classes (models) in a HTML forms environment.',
      long_description=long_description,
      author='Alexandre Conrad, Jonathan Ellis, Gaël Pasgrimaud',
      author_email='formalchemy@googlegroups.com',
      url='http://formalchemy.googlecode.com',
      download_url='http://code.google.com/p/formalchemy/downloads/list',
      install_requires=['SQLAlchemy', 'Tempita', 'WebHelpers'],
      packages=find_packages(),
      package_data={'formalchemy': ['*.tmpl', 'i18n_resources/*/LC_MESSAGES/formalchemy.mo',
                                    'ext/pylons/*.mako', 'ext/pylons/resources/*.css', 'ext/pylons/resources/*.png',
                                    'tests/data/mako/*.mako', 'tests/data/genshi/*.html',
                                    'paster_templates/pylons_fa/+package+/*/*_tmpl',
                                    ]},
      include_package_data=True,
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

