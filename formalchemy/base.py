# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import logging
logger = logging.getLogger('formalchemy.' + __name__)

from sqlalchemy import __version__
if __version__.split('.') < [0, 4, 1]:
    raise ImportError('Version 0.4.1 or later of SQLAlchemy required')

import sqlalchemy.types as types
from sqlalchemy.orm.attributes \
    import InstrumentedAttribute, _managed_attributes, ScalarAttributeImpl
from sqlalchemy.orm import compile_mappers, object_session

import utils
from options import Options


compile_mappers() # initializes InstrumentedAttributes

class Render(object):
    """The `Render` class.

    This this is the superclass for all classes needing rendering capabilities.
    The render method should be overridden with appropriate per class render
    method.

    Methods:
      * set_prettify(self, func)
      * prettify(text) (staticmethod, i.e., doesn't pass 'self')
      * render(self)

    """

    def set_prettify(self, func):
        if func is None:
            func = self.default_prettify
        if not callable(func):
            raise ValueError("Invalid callable %r" % func)
        self.prettify = func # Apply staticmethod(func) ?

    def prettify(text):
        """Return `text` prettify-ed.

        prettify("my_column_name") == "My column name"

        """
        return text.replace("_", " ").capitalize()
    default_prettify = prettify = staticmethod(prettify)

    def render(self):
        """This function must be overridden by any subclass of `Render`."""
        raise NotImplementedError()

    def __str__(self):
        return self.render()

class ModelRender(Render):
    """The `ModelRender` class.

    This this is the superclass for all classes needing to deal with `model`
    access and support rendering capabilities.

    Methods:
      * bind(self)
    """

    def __init__(self, model, session=None):
        self.options = Options()
        self.configure = self.options.configure
        self.reconfigure = self.options.reconfigure
        self.get_options = self.options.get_options
        self.new_options = self.options.new_options
        self.options.parse(model)

        self.bind(model, session)
        from fields import AttributeWrapper
        self.__dict__.update([(attr.impl.key, AttributeWrapper((attr, self.model, self.session))) 
                               for attr in _managed_attributes(self.model.__class__)
                               if isinstance(attr.impl, ScalarAttributeImpl)]) # todo support collections (i.e., any InstrumentedAttribute)
            
    def bind(self, model, session=None):
        self.model = model
        if session:
            self.session = session
        else:
            self.session = object_session(self.model)
        for attr in self._raw_attrs():
            attr.model = model

    def _raw_attrs(self):
        from fields import AttributeWrapper
        wrappers = [attr for attr in self.__dict__.itervalues()
                    if isinstance(attr, AttributeWrapper)]
        # sort by name for reproducibility
        wrappers.sort(key=lambda wrapper: wrapper.name)
        return wrappers
    
    def get_attrs(self, **kwargs):
        """Return a list of filtered attributes.

        Keyword arguments:
          * `pk=True` - Won't return primary key attributes if set to `False`.
          * `exclude=[]` - An iterable containing attributes to exclude.
          * `include=[]` - An iterable containing attributes to include.
          * `options=[]` - An iterable containing options to apply to attributes.

        Note that, when `include` is non-empty, it will
        take precedence over the other options.

        """
        pk = kwargs.get("pk", True)
        exclude = kwargs.get("exclude", [])
        include = kwargs.get("include", [])
        options = kwargs.get("options", [])
        
        if include and exclude:
            raise Exception('Specify at most one of include, exclude')

        for lst in ['include', 'exclude', 'options']:
            try:
                utils.validate_columns(eval(lst))
            except:
                raise ValueError('%s parameter should be an iterable of AttributeWrapper objects; was %s' % (lst, eval(lst)))

        if not include:
            ignore = list(exclude)
            if not pk:
                ignore.extend(self.get_pks())
            ignore.extend([wrapper for wrapper in self._raw_attrs() if wrapper.is_raw_foreign_key()])
            logger.debug('ignoring %s' % ignore)
    
            include = [attr for attr in self._raw_attrs() if attr not in ignore]
            
        # this feels overcomplicated
        options_dict = {}
        options_dict.update([(wrapper, wrapper) for wrapper in options])
        L = []
        for wrapper in include:
            if wrapper in options_dict:
                L.append(options_dict[wrapper])
            else:
                L.append(wrapper)
        return L

    def render(self):
        """This function must be overridden by any subclass of `ModelRender`."""
        raise NotImplementedError()


class ColumnRender(ModelRender):
    """The `ColumnRender` class.

    This should be the superclass for all classes that want attribute-level
    rendering. Takes an extra `attr=None` keyword argument as the concerned
    attribute.

    Methods:
      * set_column(self, attr)

    """

    def __init__(self, model, session=None, attr=None):
        super(ColumnRender, self).__init__(model, session)
        if attr:
            self.set_attr(attr)
        else:
            self.wrapper = None

    def set_attr(self, wrapper):
        """Set the column to render."""
        from fields import AttributeWrapper
        if not isinstance(wrapper, AttributeWrapper):
            raise ValueError("AttributeWrapper object expected; found %s of type %s instead." % (repr(wrapper), type(wrapper)))
        self.wrapper = wrapper
