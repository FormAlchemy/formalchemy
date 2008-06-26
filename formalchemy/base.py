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
from sqlalchemy.orm.attributes import InstrumentedAttribute, ScalarAttributeImpl
from sqlalchemy.orm import compile_mappers, object_session, class_mapper
from sqlalchemy.util import OrderedDict

import utils


compile_mappers() # initializes InstrumentedAttributes


try:
    # 0.5
    from sqlalchemy.orm.attributes import manager_of_class
    def _managed_attributes(cls):
        manager = manager_of_class(cls)
        return [manager[p.key] for p in class_mapper(cls).iterate_properties]
except ImportError:
    # 0.4
    def _managed_attributes(cls):
        return [getattr(cls, p.key) for p in class_mapper(cls).iterate_properties]
    

def _validate_columns(iterable):
    try:
        L = list(iterable)
    except:
        raise ValueError()
    from fields import AbstractField
    if L and not isinstance(L[0], AbstractField):
        raise ValueError()


class ModelRenderer(object):
    """
    The `ModelRenderer` class is the superclass for all classes needing to deal with `model`
    access and supporting rendering capabilities.
    """
    def __init__(self, model, session=None, data={}):
        """ 
        !FormAlchemy FieldSet and Table constructors take three parameters:
        
          * `model`:
                a SQLAlchemy mapped class or instance
          * `session=None`:
                the session to use for queries (for relations). If `model` is
                associated with a session, that will be used by
                default. (Objects mapped with a
                [http://www.sqlalchemy.org/docs/04/session.html#unitofwork_contextual
                scoped_session] will always have a session. Other objects will
                also have a session if they were loaded by a Query.)
          * `data={}`:
                dictionary of user-submitted data to validate and/or sync to
                the `model`. Scalar attributes should have a single value in
                the dictionary; multi-valued relations should have a list,
                even if there are zero or one values submitted.
        
        Only the `model` parameter is required.
        
        All of these parameters may be overridden by the `bind` or `rebind`
        methods.  The `bind` method returns a new instance bound as specified,
        while `rebind` modifies the current `FieldSet` or `Table` and has no
        return value. (You may not `bind` to a different type of SQLAlchemy
        model than the initial one -- if you initially bind to a `User`, you
        must subsequently bind `User`s to that `FieldSet`.)
        
        Typically, you will configure a `FieldSet` or `Table` once in a common
        form library, then `bind` specific instances later for editing.  (The
        `bind` method is thread-safe; `rebind` is not.)  Thus:
        
        {{{
        # library.py
        fs = FieldSet(User)
        fs.configure(...)
        
        # controller.py
        from library import fs
        user = session.query(User).get(id)
        fs2 = fs.bind(user)
        fs2.render()
        }}}
        
        The `fields` attribute is an OrderedDict of all the `Field`s the
        ModelRenderer knows about. The order of the fields is the order they
        were declared in the SQLAlchemy model class.
        
        The `render_fields` attribute is an OrderedDict of all the `Field`s
        that have been configured. The order of the fields is the order in
        `include`, or the order in `fields` if no `include` is specified.
        
        Note that although equivalent `Field`s (fields referring to the same
        attribute on the SQLAlchemy model) will equate with the == operator,
        the versions in `fields` are the original, unmodified ones, and the
        versions in `render_fields` have all the transforms from `configure`
        applied.
        """
        self.fields = OrderedDict()
        self._render_fields = OrderedDict()
        self.model = self.session = None

        self.rebind(model, session, data)
        from fields import AttributeField
        
        # two step process so we get the right order in the OrderedDict
        L = []
        for iattr in _managed_attributes(type(self.model)):
            if hasattr(iattr.property, 'mapper') and len(iattr.property.mapper.primary_key) != 1:
                logger.warn('ignoring multi-column property %s' % iattr.impl.key)
            else:
                L.append(AttributeField(iattr, self))
        L.sort(lambda a, b: cmp(not a.is_vanilla(), not b.is_vanilla())) # note, key= not used for 2.3 support
        for field in L:
            self.fields[field.key] = field
                
    def add(self, field):
        """Add a form Field.  By default, this Field will be included in the rendered form or table."""
        from fields import Field
        if not isinstance(field, Field):
            raise ValueError('Can only add Field objects; got %s instead' % field)
        field.parent = self
        self.fields[field.name] = field
                
    def render_fields(self):
        """The set of attributes that will be rendered"""
        if not self._render_fields:
            self._render_fields = OrderedDict([(field.name, field) for field in self._get_fields()])
        return self._render_fields
    render_fields = property(render_fields)
                
    def configure(self, pk=False, exclude=[], include=[], options=[]):
        """
        The `configure` method specifies a set of attributes to be rendered.
        By default, all attributes are rendered except primary keys and
        foreign keys.  But, relations _based on_ foreign keys _will_ be
        rendered.  For example, if an `Order` has a `user_id` FK and a `user`
        relation based on it, `user` will be rendered (as a select box of
        `User`s, by default) but `user_id` will not.
        
        Parameters:
          * `pk=False`:
                set to True to include primary key columns
          * `exclude=[]`:
                an iterable of attributes to exclude.  Other attributes will
                be rendered normally
          * `include=[]`:
                an iterable of attributes to include.  Other attributes will
                not be rendered
          * `options=[]`:
                an iterable of modified attributes.  The set of attributes to
                be rendered is unaffected
          * `global_validator=None`: `
                global_validator` should be a function that performs
                validations that need to know about the entire form.
          * `focus=True`:
                the attribute (e.g., `fs.orders`) whose rendered input element
                gets focus. Default value is True, meaning, focus the first
                element. False means do not focus at all.
        
        Only one of {`include`, `exclude`} may be specified.
        
        Note that there is no option to include foreign keys.  This is
        deliberate.  Use `include` if you really need to manually edit FKs.
        
        If `include` is specified, fields will be rendered in the order given
        in `include`.  Otherwise, fields will be rendered in alphabetical
        order.
        
        Examples: given a `FieldSet` `fs` bound to a `User` instance as a
        model with primary key `id` and attributes `name` and `email`, and a
        relation `orders` of related Order objects, the default will be to
        render `name`, `email`, and `orders`. To render the orders list as
        checkboxes instead of a select, you could specify
        
        {{{
        fs.configure(options=[fs.orders.checkbox()])
        }}}
        
        To render only name and email,
        
        {{{
        fs.configure(include=[fs.name, fs.email])
        # or
        fs.configure(exclude=[fs.options])
        }}}
        
        Of course, you can include modifications to a field in the `include`
        parameter, such as here, to render name and options-as-checkboxes:
          
        {{{
        fs.configure(include=[fs.name, fs.options.checkbox()])
        }}}
        """
        self._render_fields = OrderedDict([(field.name, field) for field in self._get_fields(pk, exclude, include, options)])

    def bind(self, model, session=None, data={}):
        """ 
        Return a copy of this FieldSet or Table, bound to the given
        `model`, `session`, and `data`. The parameters to this method are the
        same as in the constructor.
        
        Often you will create and `configure` a FieldSet or Table at application
        startup, then `bind` specific instances to it for actual editing or display.
        """
        # copy.copy causes a stacktrace on python 2.5.2/OSX + pylons.  unable to reproduce w/ simpler sample.
        mr = object.__new__(self.__class__)
        mr.__dict__ = dict(self.__dict__)
        # two steps so bind's error checking can work
        mr.rebind(model, session, data)
        mr.fields = dict([(key, renderer.bind(mr)) for key, renderer in self.fields.iteritems()])
        if self._render_fields:
            mr._render_fields = OrderedDict([(field.name, field) for field in 
                                             [field.bind(mr) for field in self._render_fields.itervalues()]])
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
        for field in self.render_fields.itervalues():
            field.sync()

    def _raw_fields(self):
        return self.fields.values()
    
    def _get_fields(self, pk=False, exclude=[], include=[], options=[]):
        if include and exclude:
            raise Exception('Specify at most one of include, exclude')

        if pk not in [True, False]:
            # help people who meant configure(include=[X]) but just wrote configure(X), resulting in pk getting the positional argument
            raise ValueError('pk option must be True or False, not %s' % pk)
            
        for lst in ['include', 'exclude', 'options']:
            try:
                _validate_columns(eval(lst))
            except:
                raise ValueError('%s parameter should be an iterable of AbstractField objects; was %s' % (lst, eval(lst)))

        if not include:
            ignore = list(exclude)
            if not pk:
                ignore.extend([wrapper for wrapper in self._raw_fields() if wrapper.is_pk() and not wrapper.is_collection()])
            ignore.extend([wrapper for wrapper in self._raw_fields() if wrapper.is_raw_foreign_key()])
            include = [field for field in self._raw_fields() if field not in ignore]
            
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
    
    def __getattr__(self, attrname):
        try:
            return self.fields[attrname]
        except KeyError:
            raise AttributeError
        
    def __setattr__(self, attrname, value):
        from fields import AbstractField
        if attrname not in ('fields', '__dict__') and attrname in self.fields or isinstance(value, AbstractField):
            raise AttributeError('Do not set field attributes manually.  Use add() or configure() instead')
        object.__setattr__(self, attrname, value)
        
    def render(self):
        raise NotImplementedError()


def prettify(text):
    """
    Turn an attribute name into something prettier, for a default label where none is given.
    >>> prettify("my_column_name")
    'My column name'
    """
    return text.replace("_", " ").capitalize()
