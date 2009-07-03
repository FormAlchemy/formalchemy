# -*- coding: utf-8 -*-
from formalchemy.tests import *

def test_append():
    """
    >>> fs = FieldSet(User)
    >>> fs.append(Field('added'))
    >>> fs._fields.keys()
    ['id', 'email', 'password', 'name', 'orders', 'added']
    """

def test_extend():
    """
    >>> fs = FieldSet(User)
    >>> fs.append(Field('added'))
    >>> fs._fields.keys()
    ['id', 'email', 'password', 'name', 'orders', 'added']
    """

def test_insert():
    """
    >>> fs = FieldSet(User)
    >>> fs.insert(fs.password, Field('login'))
    >>> fs.render_fields.keys()
    ['email', 'login', 'password', 'name', 'orders']

    """

