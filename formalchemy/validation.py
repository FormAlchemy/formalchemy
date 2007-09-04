# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import formalchemy.base as base

__all__ = ["Validate"]

class Validate(base.BaseModelRender):
    """The `Validate` class.

    This class is resposible for validating HTML forms and storing the values
    back in the bound model.

    Methods:
      * bind(self, model)
      * set_post(self, post)
      * validate(self)
      * store(self)

    """

    def __init__(self, bind=None, post=None):
        super(Validate, self).__init__(bind=bind)

        self._validators = FormAlchemyDict()
        if post:
            self._post = post
        else:
            self._post = None

    def bind(self, model):
        """Bind to the given `model` from which HTML field generation will be done."""
        super(Validate, self).bind(model)

        self._validators.clear()
        if hasattr(model, "FormAlchemyValidate"):
            [self._validators.__setitem__(col, model.FormAlchemyValidate.__dict__.get(col)) for col in self.get_colnames()]

    def set_post(self, post):
        self._post = post

    def get_post(self):
        return self._post

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
                setattr(self._model, col, post[col]=="True")
            else:
                setattr(self._model, col, post[col])

    def render(self, **options):
        """Return a HTML fields filled with POST params.

        This should be called whenever `validate()` fails and a form needs to be sent back to the user.

        """
        for col in get_colnames(**options):
            col
