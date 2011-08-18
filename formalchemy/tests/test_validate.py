# -*- coding: utf-8 -*-
from formalchemy.tests import *

def validate_empty():
    """
    >>> fs = FieldSet(bill)
    >>> fs.validate()
    Traceback (most recent call last):
    ...
    ValidationError: Cannot validate without binding data
    >>> fs.render() #doctest: +ELLIPSIS
    '<div>...</div>'
    """

def validate_no_field_in_data():
    """
    >>> fs = FieldSet(bill)
    >>> fs.rebind(data={})
    >>> fs.validate()
    False
    >>> fs.render() #doctest: +ELLIPSIS
    '<div>...</div>'
    """
