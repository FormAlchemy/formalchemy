# -*- coding: utf-8 -*-
from formalchemy.tests import *
from formalchemy.fields import PasswordFieldRenderer

def append():
    """
    >>> fs = FieldSet(User)
    >>> fs.append(Field('added'))
    >>> fs._fields.keys()
    ['id', 'email', 'password', 'name', 'orders', 'added']

    >>> fs = FieldSet(User)
    >>> fs.configure()
    >>> fs.append(Field('added'))
    >>> fs._fields.keys()
    ['id', 'email', 'password', 'name', 'orders']
    >>> fs._render_fields.keys()
    ['email', 'password', 'name', 'orders', 'added']
    """

def extend():
    """
    >>> fs = FieldSet(User)
    >>> fs.extend([Field('added')])
    >>> fs._fields.keys()
    ['id', 'email', 'password', 'name', 'orders', 'added']
    >>> fs._render_fields.keys()
    []
    >>> fs.added
    AttributeField(added)

    >>> fs = FieldSet(User)
    >>> fs.configure()
    >>> fs.extend([Field('added')])
    >>> fs._fields.keys()
    ['id', 'email', 'password', 'name', 'orders']
    >>> fs._render_fields.keys()
    ['email', 'password', 'name', 'orders', 'added']
    >>> fs.added
    AttributeField(added)
    """

def insert():
    """
    >>> fs = FieldSet(User)
    >>> fs.insert(fs.password, Field('login'))
    >>> fs._fields.keys()
    ['id', 'email', 'login', 'password', 'name', 'orders']
    >>> fs._render_fields.keys()
    []
    >>> fs.login
    AttributeField(login)

    >>> fs = FieldSet(User)
    >>> fs.configure()
    >>> fs.insert(fs.password, Field('login'))
    >>> fs._fields.keys()
    ['id', 'email', 'password', 'name', 'orders']
    >>> fs._render_fields.keys()
    ['email', 'login', 'password', 'name', 'orders']
    >>> fs.login
    AttributeField(login)
    """

def delete():
    """
    >>> fs = FieldSet(User)
    >>> del fs.name #doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    RuntimeError: You try to delete a field but your form is not configured

    >>> del fs.notexist #doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    AttributeError: field notexist does not exist

    >>> fs.configure()
    >>> del fs.name
    >>> fs._fields.keys()
    ['id', 'email', 'password', 'name', 'orders']
    >>> fs._render_fields.keys()
    ['email', 'password', 'orders']

    """

def field_update():
    """
    >>> fs = FieldSet(User)
    >>> fs.insert(fs.password, Field('login'))
    >>> def validate(value, field):
    ...     if len(value) < 2: raise ValidationError('Need more than 2 chars')
    >>> fs.password.update(renderer=PasswordFieldRenderer, validate=validate)
    AttributeField(password)
    >>> fs.password.renderer
    <PasswordFieldRenderer for AttributeField(password)>
    >>> fs.password.validators # doctest: +ELLIPSIS
    [<function required at ...>, <function validate at ...>]

    >>> field = Field('password', value='passwd', renderer=PasswordFieldRenderer)
    >>> field.renderer
    <PasswordFieldRenderer for AttributeField(password)>
    >>> field.raw_value
    'passwd'
    >>> field.update(value='new_passwd')
    AttributeField(password)
    >>> field.raw_value
    'new_passwd'
    """

