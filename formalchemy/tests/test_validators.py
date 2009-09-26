# -*- coding: utf-8 -*-
from formalchemy.tests import *
from formalchemy import validators

def validator1(value, field):
    if not value:
        raise ValidationError('Must have a value')

@validators.accepts_none
def validator2(value, field):
    if not value:
        raise ValidationError('Must have a value')


def accepts_none():
    """
    >>> fs = FieldSet(bill)
    >>> fs.configure(include=[fs.name.validate(validator1)])
    >>> fs = fs.bind(data={'User-1-name':''})
    >>> fs.validate()
    True

    >>> fs = FieldSet(bill)
    >>> fs.configure(include=[fs.name.validate(validator2)])
    >>> fs = fs.bind(data={'User-1-name':''})
    >>> fs.validate()
    False
    """

