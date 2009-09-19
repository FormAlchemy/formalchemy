# -*- coding: utf-8 -*-
import sys
from formalchemy import templates

__doc__ = """
There is two configuration settings available in a global config object.

- encoding: the global encoding used by FormAlchemy to deal with unicode. Default: utf-8

- engine: A valide :class:`~formalchemy.templates.TemplateEngine`

- date_format: Used to format date fields. Default to %Y-%d-%m

- date_edit_format: Used to retrieve field order. Default to m-d-y

Here is a simple example::

    >>> from formalchemy import config
    >>> config.encoding = 'iso-8859-1'
    >>> config.encoding
    'iso-8859-1'

    >>> from formalchemy import templates
    >>> config.engine = templates.TempitaEngine

There is also a convenience method to set the configuration from a config file::

    >>> config.from_config({'formalchemy.encoding':'utf-8',
    ...                     'formalchemy.engine':'mako',
    ...                     'formalchemy.engine.options.input_encoding':'utf-8',
    ...                     'formalchemy.engine.options.output_encoding':'utf-8',
    ...                    })
    >>> config.from_config({'formalchemy.encoding':'utf-8'})
    >>> config.encoding
    'utf-8'
    >>> isinstance(config.engine, templates.MakoEngine)
    True

"""

class Config(object):
    __doc__ = __doc__
    __name__ = 'formalchemy.config'
    __file__ = __file__
    __data = dict(
        encoding='utf-8',
        date_format='%Y-%m-%d',
        date_edit_format='m-d-y',
        engine = templates.default_engine,
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

    def __set_engine(self, value):
        if isinstance(value, templates.TemplateEngine):
            self.__data['engine'] = value
        else:
            raise ValueError('%s is not a template engine')

    def _get_config(self, config, prefix):
        values = {}
        config_keys = config.keys()
        for k in config_keys:
            if k.startswith(prefix):
                v = config.pop(k)
                k = k[len(prefix):]
                values[k] = v
        return values

    def from_config(self, config, prefix='formalchemy.'):
        from formalchemy import templates
        engine_config = self._get_config(config, '%s.engine.options.' % prefix)
        for k, v in self._get_config(config, prefix).items():
            if k == 'engine':
                engine = templates.__dict__.get('%sEngine' % v.title(), None)
                if engine is not None:
                    v = engine(**engine_config)
                else:
                    raise ValueError('%sEngine does not exist' % v.title())
            self.__setattr__(k, v)

    def __repr__(self):
        return "<module 'formalchemy.config' from '%s' with values %s>" % (self.__file__, self.__data)

sys.modules['formalchemy.config'] = Config()

