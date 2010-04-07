# -*- coding: utf-8 -*-

class PkError(Exception):
    """An exception raised when a primary key conflict occur"""

class ValidationError(Exception):
    """an exception raised when the validation failed
    """
    @property
    def message(self):
        return self.args[0]
    def __repr__(self):
        return 'ValidationError(%r,)' % self.message

