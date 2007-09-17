# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import sqlalchemy.types as types
import formalchemy.exceptions as exceptions
from formalchemy.options import Options

class BaseModel(object):
    """The `BaseModel` class.

    This is the superclass for all classes needing to deal with a model.
    Takes a `model` as argument and provides convenient model methods.

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
      * get_colnames(self[, **kwargs])
      * get_readonlys(self[, **kwargs])
      * get_coltypes(self)
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
            self._model = bind
            self._current_model = bind

    def bind(self, model):
        """Bind to the given `model` from which HTML generation will be done."""

        self.options.parse(model)
        self._model = model
        self._current_model = model

    def is_bound(self):
        """Return True if bound to a model. Otherwise, return False."""
        return bool(self._model)

    def get_model(self):
        """Return the current bound model."""
        return self._model

    def is_pk(self, col):
        """Return True if `col` is a primary key column, otherwise return False."""
        return self._model.c[col].primary_key

    def get_pks(self):
        """Return a list of primary key column names."""
        return [col for col in self._model.c.keys() if self._model.c[col].primary_key]

    def is_fk(self, col):
        """Return True if `col` is a primary foreign column, otherwise return False."""
        return self._model.c[col].foreign_key

    def get_fks(self):
        """Return a list of foreign key column names."""
        return [col for col in self._model.c.keys() if self._model.c[col].foreign_key]

    def is_nullable(self, col):
        """Return True if `col` is a nullable column, otherwise return False."""
        return self._model.c[col].nullable

    def get_unnullables(self):
        """Return a list of non-nullable column names."""
        return [col for col in self._model.c.keys() if not self._model.c[col].nullable]

    def get_colnames(self, **kwargs):
        """Return a list of filtered column names.

        Keyword arguments:
          * `pk=True` - Won't return primary key columns if set to `False`.
          * `fk=True` - Won't return foreign key columns if set to `False`.
          * `exclude=[]` - An string or an iterable containing column names to exclude.

        """

        if not self.is_bound():
            raise exceptions.UnboundModelError(self.__class__)

        if kwargs:
            return self._get_filtered_cols(**kwargs)
        return self._model.c.keys()

    def _get_filtered_cols(self, **kwargs):
        pk = kwargs.get("pk", True)
        fk = kwargs.get("fk", True)
        exclude = kwargs.get("exclude", [])

        if isinstance(exclude, basestring):
            exclude = [exclude]

        ignore = exclude[:]
        if not pk:
            ignore.extend(self.get_pks())
        if not fk:
            ignore.extend(self.get_fks())

        columns = []

        for col in self.get_colnames():
            if not col in ignore:
                columns.append(col)

        return columns

    def get_readonlys(self, **kwargs):
        """Return a list of columns that should be readonly.

        Keywords arguments:
          * `readonly_pk=False` - Will prohibit changes to primary key columns if set to `True`.
          * `readonly_fk=False` - Will prohibit changes to foreign key columns if set to `True`.
          * `readonly=[]` - A string or an iterable containing column names to set as readonly.

        """

        ro_pks = kwargs.get("readonly_pk", False)
        ro_fks = kwargs.get("readonly_fk", False)
        readonlys = kwargs.get("readonly", [])

        if isinstance(readonlys, basestring):
            readonlys = [readonlys]

        if ro_pks:
            readonlys += self.get_pks()
        if ro_fks:
            readonlys += self.get_fks()

        columns = []

        for col in self.get_colnames():
            if col in readonlys:
                columns.append(col)

        return columns

    def get_coltypes(self):
        """Categorize columns by type.

        Return a eight key dict. Each key is a direct subclass of TypeEngine:
          * `Binary=[]` - a list of Binary column names.
          * `Boolean=[]` - a list of Boolean column names.
          * `Date=[]` - a list of Date column names.
          * `DateTime=[]` - a list of DateTime column names.
          * `Integer=[]` - a list of Integer column names.
          * `Numeric=[]` - a list of Numeric column names.
          * `String=[]` - a list of String column names.
          * `Time=[]` - a list of Time column names.

        """

        # FIXME: What shall we do about non-standard SQLAlchemy types that were
        # built directly off of a TypeEngine type?
        # Although, this should handle custum types built from one of those 8.

        col_types = dict.fromkeys([t for t in [
                                          types.Binary,
                                          types.Boolean,
                                          types.Date,
                                          types.DateTime,
                                          types.Integer,
                                          types.Numeric,
                                          types.String,
                                          types.Time]], [])

        for t in col_types:
            col_types[t] = [col.name for col in self._model.c if isinstance(col.type, t)]

        return col_types

    def get_type(self, string):
        """Return a list of `string` type column names.

        `string` is case insensitive.

        Valid `string` values:
          * "binary"
          * "boolean"
          * "date"
          * "datetime"
          * "integer"
          * "nulltype"
          * "numeric"
          * "string"
          * "time"

        """

        d = {
            "binary":types.Binary,
            "boolean":types.Boolean,
            "date":types.Date,
            "datetime":types.DateTime,
            "integer":types.Integer,
            "numeric":types.Numeric,
            "string":types.String,
            "time":types.Time,
        }

        return self.get_coltypes().get(d[string.lower()], [])

#    def __repr__(self):
#        repr = "%s bound to: %s" % (self.__class__.__name__, self._model)
#        return "<" + repr + ">"

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
        if callable(func):
            self.prettify = func # Apply staticmethod(func) ?
#        else:
#            raise ValueError("Invalid callable %s" % repr(func))

    def prettify(text):
        """Return `text` prettify-ed.

        prettify("my_column_name") == "My column name"

        """
        return text.replace("_", " ").capitalize()

    prettify = staticmethod(prettify)

    def render(self):
        """This function must be overridden by any subclass of `BaseRender`."""
        if self.__class__.__name__ == "BaseRender":
            raise exceptions.NotImplementedError()

    def __str__(self):
        return self.render()

class BaseModelRender(BaseModel, BaseRender):
    """The `BaseModelRender` class.

    This this is the superclass for all classes needing to deal with `model`
    access and support rendering capabilities.

    """

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

    This should be the superclass for all classes that want column level
    rendering. Takes an extra `column=None` keyword argument as the concerned
    column name.

    Methods:
      * set_column(self, col_name)
      * get_column(self)

    """

    def __init__(self, bind=None, column=None):
        super(BaseColumnRender, self).__init__(bind=bind)
        if column:
            self.set_column(column)
        else:
            self._column = None

    def set_column(self, column):
        """Set the column to render."""

        if not isinstance(column, basestring):
            raise ValueError("Column name should be a string, found %s of type %s instead." % (repr(column), type(column)))
        self._column = column

    def get_column(self):
        """Return current column."""
        return self._column

    def render(self):
        super(BaseColumnRender, self).render()
        if not isinstance(self._column, basestring):
            raise exceptions.InvalidColumnError("Invalid column '%s'. Please specify an existing column name using .set_column() before rendering." % (self._column))
