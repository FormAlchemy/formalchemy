# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import logging
logger = logging.getLogger('formalchemy.' + __name__)
from copy import copy

from sqlalchemy import __version__
if __version__.split('.') < [0, 4, 1]:
    raise ImportError('Version 0.4.1 or later of SQLAlchemy required')

import sqlalchemy.types as types
from sqlalchemy.orm.attributes import InstrumentedAttribute, ScalarAttributeImpl
from sqlalchemy.orm import compile_mappers, object_session

import utils


compile_mappers() # initializes InstrumentedAttributes

try:
    from sqlalchemy.orm.attributes import _managed_attributes
except ImportError:
    from sqlalchemy.orm.attributes import manager_of_class
    def _managed_attributes(cls):
        return manager_of_class(cls).values()
    

class ModelRender(object):
    """The `ModelRender` class.

    This this is the superclass for all classes needing to deal with `model`
    access and support rendering capabilities.

    Methods:
      * bind(self)
    """

    def __init__(self, model, session=None, data={}):
        self.model = self.session = None
        self._render_attrs = None

        self.rebind(model, session, data)
        from fields import AttributeWrapper
        
        for iattr in _managed_attributes(type(self.model)):
            if hasattr(iattr.property, 'mapper') and len(iattr.property.mapper.primary_key) != 1:
                logger.warn('ignoring multi-column property %s' % iattr.impl.key)
            else:
                setattr(self, iattr.impl.key, AttributeWrapper(iattr, self))
                
    def render_attrs(self):
        if self._render_attrs:
            return self._render_attrs
        return self.get_attrs()
    render_attrs = property(render_attrs)
                
    def configure(self, pk=False, exclude=[], include=[], options=[]):
        """configure render_attrs and any extra args for template"""
        self._render_attrs = self.get_attrs(pk, exclude, include, options)

    def bind(self, model, session=None, data={}):
        """return a copy of this object, bound to model and session"""
        # two steps so bind's error checking can work
        mr = copy(self)
        mr.rebind(model, session, data)
        for iattr in _managed_attributes(type(self.model)):
            setattr(mr, iattr.impl.key, getattr(self, iattr.impl.key).bind(mr))
        if self._render_attrs:
            mr._render_attrs = [attr.bind(mr) for attr in self._render_attrs]
        return mr

    def rebind(self, model=None, session=None, data=None):
        """rebind this object to model and session.  no return value"""
        if model:
            if isinstance(model, type):
                try:
                    model = model()
                except:
                    raise Exception('%s appears to be a class, not an instance, but FormAlchemy cannot instantiate it' % model)
                # take object out of session, if present
                s = object_session(model)
                if s:
                    s.expunge(model)
            if self.model and type(self.model) != type(model):
                raise ValueError('You can only bind to another object of the same type you originally bound to (%s), not %s' % (type(self.model), type(model)))
            self.model = model
        self.data = data
        if session:
            self.session = session
        elif model:
            self.session = object_session(model)
        if self.session and object_session(self.model):
            if self.session is not object_session(self.model):
                raise Exception('Thou shalt not rebind to different session than the one the model belongs to')

    def sync(self):
        for attr in self.render_attrs:
            attr.sync()

    def _raw_attrs(self):
        from fields import AttributeWrapper
        wrappers = [attr for attr in self.__dict__.itervalues()
                    if isinstance(attr, AttributeWrapper)]
        # sort by name for reproducibility
        try:
            wrappers.sort(key=lambda wrapper: wrapper.name)
        except TypeError:
            # 2.3 support
            wrappers.sort(lambda a, b: cmp(a.name, b.name))
        return wrappers
    
    def get_attrs(self, pk=False, exclude=[], include=[], options=[]):
        """Return a list of filtered attributes.

        Keyword arguments:
          * `pk=False` - Include primary key attributes if set to `True`.
          * `exclude=[]` - An iterable containing attributes to exclude.
          * `include=[]` - An iterable containing attributes to include.
          * `options=[]` - An iterable containing options to apply to attributes.

        Note that when `include` is non-empty, it will
        take precedence over the other options.

        """
        if include and exclude:
            raise Exception('Specify at most one of include, exclude')

        if pk not in [True, False]:
            # help people who meant configure(include=[X]) but just wrote configure(X), resulting in pk getting the positional argument
            raise ValueError('pk option must be True or False, not %s' % pk)
            
        for lst in ['include', 'exclude', 'options']:
            try:
                utils.validate_columns(eval(lst))
            except:
                raise ValueError('%s parameter should be an iterable of AttributeWrapper objects; was %s' % (lst, eval(lst)))

        if not include:
            ignore = list(exclude)
            if not pk:
                ignore.extend([wrapper for wrapper in self._raw_attrs() if wrapper.is_pk() and not wrapper.is_collection()])
            ignore.extend([wrapper for wrapper in self._raw_attrs() if wrapper.is_raw_foreign_key()])
            include = [attr for attr in self._raw_attrs() if attr not in ignore]
            
        # this feels overcomplicated
        options_dict = {}
        options_dict.update(dict([(wrapper, wrapper) for wrapper in options]))
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


def prettify(text):
    """
    Turn an attribute name into something prettier, for a default label where none is given.
    >>> prettify("my_column_name")
    'My column name'
    """
    return text.replace("_", " ").capitalize()
