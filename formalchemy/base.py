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
from sqlalchemy.orm import compile_mappers, object_session

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
        raise exceptions.NotImplementedError()

    def __str__(self):
        return self.render()

class BaseModelRender(BaseRender):
    """The `BaseModelRender` class.

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
        BaseModelRender.bind(self, model, session) # hack to force subclass bind to not be called here
            
    def bind(self, model, session=None):
        self.model = self._current_model = model
        if session:
            self.session = session
        else:
            self.session = object_session(self.model)

    def render(self):
        """This function must be overridden by any subclass of `BaseModelRender`."""
        raise exceptions.NotImplementedError()

class BaseCollectionRender(BaseModelRender):
    """The `BaseCollectionRender` class.

    This is the superclass for all classes needing collection rendering. Takes
    an extra `collection=[]` keyword argument as the collection list.

    Methods:
      * set_collection(self, collection)
      * get_collection(self)

    """

    def __init__(self, model, collection=[]):
        super(BaseCollectionRender, self).__init__(model)
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

    def __init__(self, model, session=None, attr=None):
        super(BaseColumnRender, self).__init__(model, session)
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
