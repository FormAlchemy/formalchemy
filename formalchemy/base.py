# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy import __version__
if __version__.split('.') < [0, 4, 1]:
    raise ImportError('Version 0.4.1 or later of SQLAlchemy required')

from sqlalchemy.orm.attributes \
    import InstrumentedAttribute, _managed_attributes, ScalarAttributeImpl
import sqlalchemy.types as types
from sqlalchemy.orm import compile_mappers

import exceptions, utils
from options import Options


compile_mappers() # initializes InstrumentedAttributes

class BaseRender(object):
    """The `BaseRender` class.

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
        """This function must be overridden by any subclass of `BaseRender`."""
        if self.__class__.__name__ == "BaseRender":
            raise exceptions.NotImplementedError()

    def __str__(self):
        return self.render()

class BaseModelRender(BaseRender):
    """The `BaseModelRender` class.

    This this is the superclass for all classes needing to deal with `model`
    access and support rendering capabilities.

    Methods:
      * bind(self, model)
      * is_bound(self)
      * get_model(self)
      * is_pk(self, col)
      * get_pks(self)
      * is_fk(self, col)
      * get_fks(self)
      * is_nullable(self, col)
      * get_unnullables(self)
      * get_attrs(self[, **kwargs])
      * get_readonlys(self[, **kwargs])
      * get_bytype(self, string)
    """

    def __init__(self, bind=None):
        self.options = Options()
        self.configure = self.options.configure
        self.reconfigure = self.options.reconfigure
        self.get_options = self.options.get_options
        self.new_options = self.options.new_options

        if bind:
            self.bind(bind)
        else:
            self.model = bind
            self._current_model = bind

    def bind(self, model):
        """Bind to the given `model` from which HTML generation will be done."""

        self.options.parse(model)
        self.model = model
        self._current_model = model

    def is_bound(self):
        """Return True if bound to a model. Otherwise, return False."""
        return bool(self.model)

    def get_model(self):
        """Return the current bound model."""
        return self.model

    def get_pks(self):
        """Return a list of primary key attributes."""
        return [wrapper for wrapper in self.get_attrs() if wrapper.column.primary_key]

    def get_fks(self):
        """Return a list of foreign key attributes."""
        return [wrapper for wrapper in self.get_attrs() if wrapper.column.foreign_key]

    def get_unnullables(self):
        """Return a list of non-nullable attributes."""
        return [wrapper for wrapper in self.get_attrs() if wrapper.column.nullable]

    def get_attrs(self, **kwargs):
        """Return a list of filtered attributes.

        Keyword arguments:
          * `pk=True` - Won't return primary key attributes if set to `False`.
          * `fk=True` - Won't return foreign key attributes if set to `False`.
          * `exclude=[]` - An iterable containing attributes to exclude.
          * `include=[]` - An iterable containing attributes to include.
          * `options=[]` - An iterable containing options to apply to attributes.

        Note that, when `include` is non-empty, it will
        take precedence over the other options.

        """
        from fields import AttributeWrapper
        if not self.is_bound():
            raise exceptions.UnboundModelError(self.__class__)

        if kwargs:
            wrappers = self._get_filtered_attrs(**kwargs)
        else:
            wrappers = [AttributeWrapper(attr) for attr in _managed_attributes(self.model.__class__)
                     if isinstance(attr.impl, ScalarAttributeImpl)
                     and hasattr(attr.property, 'columns')
                     and len(attr.property.columns) == 1]
            # sort by name for reproducibility
            wrappers.sort(key=lambda wrapper: wrapper.name)
        return wrappers

    def _get_filtered_attrs(self, **kwargs):
        pk = kwargs.get("pk", True)
        fk = kwargs.get("fk", True)
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
            if not fk:
                ignore.extend(self.get_fks())
    
            include = [attr for attr in self.get_attrs() if attr not in ignore]
            
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

    def get_readonlys(self, **kwargs):
        """Return a list of attributes that should be readonly.

        Keywords arguments:
          * `readonly_pk=False` - Will prohibit changes to primary key attributes if set to `True`.
          * `readonly_fk=False` - Will prohibit changes to foreign key attributes if set to `True`.
          * `readonly=[]` - An iterable containing attributes to set as readonly.

        """

        ro_pks = kwargs.get("readonly_pk", False)
        ro_fks = kwargs.get("readonly_fk", False)
        readonlys = kwargs.get("readonly", [])

        try:
            utils.validate_columns(readonlys)
        except:
            raise ValueError('readonlys parameter should be an iterable of AttributeWrapper objects; was %s' % (readonlys,))

        if ro_pks:
            readonlys.extend(self.get_pks())
        if ro_fks:
            readonlys.extend(self.get_fks())

        return readonlys

    def get_disabled(self, **kwargs):
        """Return a list of attributes that should be disabled.

        Keywords arguments:
          * `disable_pk=False` - Will prohibit changes to primary key attributes if set to `True`.
          * `disable_fk=False` - Will prohibit changes to foreign key attributes if set to `True`.
          * `disable=[]` - An iterable containing attributes to set as disabled.

        """

        dis_pks = kwargs.get("disable_pk", False)
        dis_fks = kwargs.get("disable_fk", False)
        disabled = kwargs.get("disable", [])

        try:
            utils.validate_columns(disabled)
        except:
            raise ValueError('disabled parameter should be an iterable of AttributeWrapper objects; was %s' % (disabled,))

        if dis_pks:
            disabled.extend(self.get_pks())
        if dis_fks:
            disabled.extend(self.get_fks())

        return disabled

    def render(self):
        """This function must be overridden by any subclass of `BaseModelRender`."""
        if self.__class__.__name__ == "BaseModelRender":
            raise exceptions.NotImplementedError()

        if not self.is_bound():
             raise exceptions.UnboundModelError(self.__class__)

class BaseCollectionRender(BaseModelRender):
    """The `BaseCollectionRender` class.

    This is the superclass for all classes needing collection rendering. Takes
    an extra `collection=[]` keyword argument as the collection list.

    Methods:
      * set_collection(self, collection)
      * get_collection(self)

    """

    def __init__(self, bind=None, collection=[]):
        super(BaseCollectionRender, self).__init__(bind=bind)
        self.collection = collection

    def set_collection(self, collection):
        """Set the collection to render."""

        if not isinstance(collection, (list, tuple)):
            raise exceptions.InvalidCollectionError()
        self.collection = collection

    def get_collection(self):
        """Return current collection."""
        return self.collection


class BaseColumnRender(BaseModelRender):
    """The `BaseColumnRender` class.

    This should be the superclass for all classes that want attribute-level
    rendering. Takes an extra `attr=None` keyword argument as the concerned
    attribute.

    Methods:
      * set_column(self, attr)

    """

    def __init__(self, bind=None, attr=None):
        super(BaseColumnRender, self).__init__(bind=bind)
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
