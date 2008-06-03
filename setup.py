from distutils.core import setup
setup(name='FormAlchemy',
      license='MIT License',
      version='0.3',
      description='FormAlchemy greatly speeds development with SQLAlchemy mapped classes (models) in a HTML forms environment.',
      long_description="""FormAlchemy eliminates boilerplate by autogenerating HTML input fields from a
given model. FormAlchemy will try to figure out what kind of HTML code should
be returned by introspecting the model's properties and generate ready-to-use
HTML code that will fit the developer's application.

Of course, FormAlchemy can't figure out everything, i.e, the developer might
want to display only a few columns from the given model. Thus, FormAlchemy is
also highly customizable.""",
      author='Alexandre Conrad',
      author_email='aconard at go2france dot com',
      url='http://formalchemy.googlecode.com',
      download_url='http://code.google.com/p/formalchemy/downloads/list',
      packages=['formalchemy', 'formalchemy.tempita'],
      classifiers=[
          'Development Status :: 3 - Alpha',
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
