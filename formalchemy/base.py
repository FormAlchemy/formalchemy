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
    

class ModelRenderer(object):
    """
    The `ModelRenderer` class is the superclass for all classes needing to deal with `model`
    access and supporting rendering capabilities.
    """

    def __init__(self, model, session=None, data={}):
        """ 
          * `model`: a SQLAlchemy mapped class or instance 
          * `session`: the
            session to use for queries (for relations). If `model` is associated
            with a session, that will be used by default. (Objects mapped with a
            scoped_session will always have a session. Other objects will also
            have a session if they were loaded by a Query.) 
           * `data`: dictionary
            of user-submitted data to validate and/or sync to the `model`. Scalar
            attributes should have a single value in the dictionary; multi-valued
            relations should have a list, even if there are zero or one values
            submitted. 
        """
        self.model = self.session = None
        self._render_attrs = None

        self.rebind(model, session, data)
        from fields import AttributeRenderer
        
        for iattr in _managed_attributes(type(self.model)):
            if hasattr(iattr.property, 'mapper') and len(iattr.property.mapper.primary_key) != 1:
                logger.warn('ignoring multi-column property %s' % iattr.impl.key)
            else:
                setattr(self, iattr.impl.key, AttributeRenderer(iattr, self))
                
    def render_attrs(self):
        """The set of attributes that will be rendered"""
        if self._render_attrs:
            return self._render_attrs
        return self._get_attrs()
    render_attrs = property(render_attrs)
                
    def configure(self, pk=False, exclude=[], include=[], options=[]):
        """
        Configures attributes to be rendered.  By default, all attributes are rendered except
        primary keys and foreign keys.  (But, relations _based on_ foreign keys _will_ be rendered.
        For example, if an `Order` has a `user_id` FK and a `user` relation based on it,
        `user` will be rendered (as a select box of `User`s, by default) but `user_id` will not.)
        
        Options:
          * `pk`: set to True to include primary key columns
          * `exclude`: an iterable of attributes to exclude.  Other attributes will be rendered normally
          * `include`: an iterable of attributes to include.  Other attributes will not be rendered
          * `options`: an iterable of modified attributes.  The set of attributes to be rendered is unaffected
        Only one of {`include`, `exclude`} may be specified.
        
        Note that there is no option to include foreign keys.  This is deliberate.  Use `include` if
        you really need to manually edit FKs.
        
        Examples: given a FieldSet fs bound to a `User` instance as a model with
        primary key `id` and attributes `name` and `email`, and a relation
        `orders` of related Order objects, the default will be to render
        `name`, `email`, and `orders`. To render the orders list as checkboxes
        instead of a select, you could specify
        
        fs.configure(options=[fs.orders.checkbox()])
        
        To render only name and email,
        
        fs.configure(include=[fs.name, fs.email]) -- or, fs.configure(exclude=[fs.options])
        
        To render name and options-as-checkboxes,
          
        fs.configure(include=[fs.name, fs.options.checkbox()])
        """
        self._render_attrs = self._get_attrs(pk, exclude, include, options)

    def bind(self, model, session=None, data={}):
        """ 
        Return a copy of this FieldSet or Table, bound to the given
        `model`, `session`, and `data`. The parameters to this method are the
        same as in the constructor.
        
        Often you will create and `configure` a FieldSet or Table at application
        startup, then `bind` specific instances to it for actual editing or display.
        """
        # two steps so bind's error checking can work
        mr = copy(self)
        mr.rebind(model, session, data)
        for iattr in _managed_attributes(type(self.model)):
            setattr(mr, iattr.impl.key, getattr(self, iattr.impl.key).bind(mr))
        if self._render_attrs:
            mr._render_attrs = [attr.bind(mr) for attr in self._render_attrs]
        return mr

    def rebind(self, model=None, session=None, data=None):
        """Like `bind`, but acts on this instance.  No return value."""
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
        """
        Sync (copy to the corresponding attributes) the data passed to the constructor or `bind` to the `model`.
        """
        for attr in self.render_attrs:
            attr.sync()

    def _raw_attrs(self):
        from fields import AttributeRenderer
        wrappers = [attr for attr in self.__dict__.itervalues()
                    if isinstance(attr, AttributeRenderer)]
        # sort by name for reproducibility
        try:
            wrappers.sort(key=lambda wrapper: wrapper.name)
        except TypeError:
            # 2.3 support
            wrappers.sort(lambda a, b: cmp(a.name, b.name))
        return wrappers
    
    def _get_attrs(self, pk=False, exclude=[], include=[], options=[]):
        if include and exclude:
            raise Exception('Specify at most one of include, exclude')

        if pk not in [True, False]:
            # help people who meant configure(include=[X]) but just wrote configure(X), resulting in pk getting the positional argument
            raise ValueError('pk option must be True or False, not %s' % pk)
            
        for lst in ['include', 'exclude', 'options']:
            try:
                utils.validate_columns(eval(lst))
            except:
                raise ValueError('%s parameter should be an iterable of AttributeRenderer objects; was %s' % (lst, eval(lst)))

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
        raise NotImplementedError()


def prettify(text):
    """
    Turn an attribute name into something prettier, for a default label where none is given.
    >>> prettify("my_column_name")
    'My column name'
    """
    return text.replace("_", " ").capitalize()
