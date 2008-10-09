# -*- coding: utf-8 -*-

long_description = open('README.txt').read().strip() +\
                   '\n\n' +\
                   'Changes\n' +\
                   '=======\n\n' +\
                   open('CHANGELOG.txt').read().strip()

args = dict(name='FormAlchemy',
      license='MIT License',
      version='1.0',
      description='FormAlchemy greatly speeds development with SQLAlchemy mapped classes (models) in a HTML forms environment.',
      long_description=long_description,
      author='Alexandre Conrad, Jonathan Ellis, Gaël Pasgrimaud',
      author_email='formalchemy@googlegroups.com',
      url='http://formalchemy.googlecode.com',
      download_url='http://code.google.com/p/formalchemy/downloads/list',
      packages=['formalchemy', 'formalchemy.tempita'],
      package_data={'formalchemy': ['i18n/*/LC_MESSAGES/formalchemy.mo']},
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
      ]
)

try:
    from setuptools import setup
    args.update(
          message_extractors = {'formalchemy': [
                  ('**.py', 'python', None),
                  ('**.mako', 'mako', None)]},
          zip_safe=False,
          )
except:
    from distutils.core import setup

setup(**args)

