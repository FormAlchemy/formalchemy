# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import formalchemy.base as base
import sqlalchemy.types as types

__all__ = ["Validate", "Populate"]
__doc__ = """

from sqlalchemy import *
from sqlalchemy.orm import *

meta = MetaData()

user_table = Table('users', meta,
    Column('id', Integer, primary_key=True),
    Column('email', Unicode(40), unique=True, nullable=False),
    Column('password', Unicode(20), nullable=False),
    Column('first_name', Unicode(20)),
    Column('last_name', Unicode(20)),
    Column('description', Unicode),
    Column('active', Boolean, default=True),
)

class User(object):
    pass

mapper(User, user_table)

user = User()

class User(object):
    class FormAlchemy:
        class Validate:
            email = 
            messages = {
                "email":
            }

"""

class Populate(base.BaseModelRender):
    """The `Populate` class.

    This class is responsible for populating a model from a given POST.

    """

    def __init__(self, bind=None, post=None):
        super(Populate, self).__init__(bind=bind)
        self.post = post

    def populate(self, **kwargs):
        # Hold a list of column names by type.
        col_types = self.get_coltypes()

#        for param in self.post:
#            if param in self.get_colnames():
#                print "Parsing", param, repr(self.post[param]), "#" * 30
#                if param in col_types[types.Boolean]:
#                    print self.post[param] == "True", "BOOL", "#" * 10
#                    setattr(self.model, param, self.post[param] == "True")
#                else:
#                    setattr(self.model, param, self.post[param] or None)

        for column in self.get_colnames(**kwargs):
            print "Parsing column", column, "#" * 15
            if column in self.post:
                print "  ", column, repr(self.post.get(column))
                if column in col_types[types.Boolean]:
                    print "    ", "setting boolean column", column, "to", repr(self.post.get(column) == "True")
                    setattr(self.model, column, self.post.get(column) == "True")
                else:
                    print "    ", "setting column", column, "to", repr(self.post.get(column) or None)
                    setattr(self.model, column, self.post.get(column) or None)

class Validate(base.BaseModelRender):
    """The `Validate` class.

    This class is responsible for validating HTML forms and storing the values
    back in the bound model.

    Methods:
      * bind(self, model)
      * validate(self)
      * store(self)

    """

    def __init__(self, bind=None, post=None):
        super(Validate, self).__init__(bind=bind)

        self._validators = FormAlchemyDict()
        self.post = None

    def bind(self, model):
        """Bind to the given `model` from which HTML field generation will be done."""
        super(Validate, self).bind(model)

        self._validators.clear()
        if hasattr(model, "FormAlchemyValidate"):
            [self._validators.__setitem__(col, model.FormAlchemyValidate.__dict__.get(col)) for col in self.get_colnames()]

    def _test_func_value(func, value):
        if callable(func):
            return func(value)
        return True

    _test_func_value = staticmethod(_test_func_value)

    def validate(self):
        """Validate the model against the POST request `post`."""
        for col in self.get_colnames():

            # Skip columns that were not sent in POST.
            if not col in post:
                continue

            func = self._validators.get(col)
            value = post[col]
            if not _test_func_value(func, value):
                return False

        return True

    def store(self):
        # Hold a list of column names by type.
        col_types = self.get_coltypes()

        for col in self.get_colnames():

            # Columns not in POST will be kept intact.
            if not col in post:
                continue

            if col in col_types[Boolean]:
                setattr(self.model, col, post[col]=="True")
            else:
                setattr(self.model, col, post[col])

    def render(self, **options):
        """Return a HTML fields filled with POST params.

        This should be called whenever `validate()` fails and a form needs to be sent back to the user.

        """
        for col in get_colnames(**options):
            col
