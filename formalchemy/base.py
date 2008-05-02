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


compile_mappers() # initializes InstrumentedAttributes

def prettify(text):
    """
    Return `text` prettify-ed.
    >>> prettify("my_column_name")
    "My column name"
    """
    return text.replace("_", " ").capitalize()

class ModelRender(object):
    """The `ModelRender` class.

    This this is the superclass for all classes needing to deal with `model`
    access and support rendering capabilities.

    Methods:
      * bind(self)
    """

    def __init__(self, model, session=None):
        self.model = self.session = None
        self.options = {}

        self.rebind(model, session)
        from fields import AttributeWrapper
        
        for iattr in _managed_attributes(self.model.__class__):
            if hasattr(iattr.property, 'mapper') and len(iattr.property.mapper.primary_key) != 1:
                logger.warn('ignoring multi-column property %s' % iattr.impl.key)
            else:
                setattr(self, iattr.impl.key, AttributeWrapper((iattr, self.model, self.session)))
                
    def configure(self, **options):
        self.options.update(options)

    def reconfigure(self, **options):
        self.options.clear()
        self.options.update(options)
            
    def bind(self, model, session=None):
        # two steps so bind's error checking can work
        copy = type(self)(self.model, self.session)
        copy.rebind(model, session)
        copy.configure(**self.options)
        return copy

    def rebind(self, model, session=None):
        if isinstance(model, type):
            try:
                model = model()
                # take object out of session, if present
                s = object_session(model)
                if s:
                    s.expunge(model)
            except:
                raise Exception('%s appears to be a class, not an instance, but FormAlchemy cannot instantiate it' % model)
        if self.model and type(self.model) != type(model):
            raise ValueError('You can only bind to another object of the same type you originally bound to (%s), not %s' % (type(self.model), type(model)))
        self.model = model
        if session:
            self.session = session
        else:
            self.session = object_session(model)
        for attr in self._raw_attrs():
            attr.model = model
            attr.session = self.session

    def get_pks(self):
        """Return a list of primary key attributes."""
        return [wrapper for wrapper in self._raw_attrs() if wrapper.column.primary_key and not wrapper.is_collection()]

    def get_required(self):
        """Return a list of non-nullable attributes."""
        return [wrapper for wrapper in self._raw_attrs() if not wrapper.column.nullable]

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
          * `pk=False` - Include primary key attributes if set to `True`.
          * `exclude=[]` - An iterable containing attributes to exclude.
          * `include=[]` - An iterable containing attributes to include.
          * `options=[]` - An iterable containing options to apply to attributes.

        Note that, when `include` is non-empty, it will
        take precedence over the other options.

        """
        pk = kwargs.get("pk", False)
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
