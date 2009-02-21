# -*- coding: utf-8 -*-
import sys
from formalchemy import templates

class Config(object):
    """A class to store global configuration::

        >>> from formalchemy import config
        >>> config.encoding = 'iso-8859-1'
        >>> config.encoding
        'iso-8859-1'

        >>> config.from_config({'formalchemy.encoding':'utf-8'})
        >>> config.encoding
        'utf-8'

    """
    __name__ = 'formalchemy.config'
    __file__ = __file__
    __data = dict(
        encoding='utf-8',
        template_engine = templates.default_engine,
    )

    def __getattr__(self, attr):
        if attr in self.__data:
            return self.__data[attr]
        else:
            raise AttributeError('Configuration has no attribute %s' % attr)

    def __setattr__(self, attr, value):
        meth = getattr(self, '__set_%s' % attr, None)
        if callable(meth):
            meth(value)
        else:
            self.__data[attr] = value

    def __set_template_engine(self, value):
        if isinstance(value, templates.TemplateEngine):
            self.__data['template_engine'] = value
        else:
            raise ValueError('%s is not a template engine')

    def from_config(self, config, prefix='formalchemy.'):
        for k, v in config.items():
            if k.startswith(prefix):
                k = k[len(prefix):]
                self.__setattr__(k, v)

    def __repr__(self):
        return "<module 'formalchemy.config' from '%s' with values %s>" % (self.__file__, self.__data)

sys.modules['formalchemy.config'] = Config()

