# -*- coding: utf-8 -*-
from formalchemy.tests import *
from formalchemy.fields import PasswordFieldRenderer

def copy():
    """
    >>> fs = FieldSet(User)
    >>> fs1 = fs.copy(fs.id, fs.email)
    >>> fs1._render_fields.keys()
    ['id', 'email']
    >>> fs2 = fs.copy(fs.name, fs.email)
    >>> fs2._render_fields.keys()
    ['name', 'email']
    """

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

def test_insert_after_relation():
    """
    >>> fs = FieldSet(OTOParent)
    >>> fs.configure()
    >>> fs.insert(fs.child, Field('foo'))
    >>> fs.insert_after(fs.child, Field('bar'))
    >>> fs._render_fields.keys()
    ['foo', 'child', 'bar']
    """

def test_insert_after_alias():
    """
    >>> fs = FieldSet(Aliases)
    >>> fs.configure()
    >>> fs.insert(fs.text, Field('foo'))
    >>> fs.insert_after(fs.text, Field('bar'))
    >>> fs._render_fields.keys()
    ['foo', 'text', 'bar']
    """

def insert_after():
    """
    >>> fs = FieldSet(User)
    >>> fs.insert_after(fs.password, Field('login'))
    >>> fs._fields.keys()
    ['id', 'email', 'password', 'login', 'name', 'orders']
    >>> fs._render_fields.keys()
    []
    >>> fs.login
    AttributeField(login)

    >>> fs = FieldSet(User)
    >>> fs.configure()
    >>> fs.insert_after(fs.password, Field('login'))
    >>> fs._fields.keys()
    ['id', 'email', 'password', 'name', 'orders']
    >>> fs._render_fields.keys()
    ['email', 'password', 'login', 'name', 'orders']
    >>> fs.login
    AttributeField(login)

    >>> fs.insert_after('somethingbad', Field('login'))  #doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    TypeError: field must be a Field. Got 'somethingbad'
    >>> fs.insert_after(fs.password, ['some', 'random', 'objects'])  #doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: Can only add Field objects; got AttributeField(password) instead
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

def test_delete_relation():
    """
    >>> fs = FieldSet(OTOParent)
    >>> fs.configure()
    >>> del fs.child
    """

def field_set():
    """
    >>> fs = FieldSet(User)
    >>> fs.insert(fs.password, Field('login'))
    >>> def validate(value, field):
    ...     if len(value) < 2: raise ValidationError('Need more than 2 chars')
    >>> fs.password.set(renderer=PasswordFieldRenderer, validate=validate)
    AttributeField(password)
    >>> fs.password.renderer
    <PasswordFieldRenderer for AttributeField(password)>
    >>> fs.password.validators # doctest: +ELLIPSIS
    [<function required at ...>, <function validate at ...>]

    >>> fs.password.set(instructions='Put a password here')
    AttributeField(password)
    >>> fs.password.metadata
    {'instructions': 'Put a password here'}

    >>> field = Field('password', value='passwd', renderer=PasswordFieldRenderer)
    >>> field.renderer
    <PasswordFieldRenderer for AttributeField(password)>
    >>> field.raw_value
    'passwd'

    >>> field.set(value='new_passwd')
    AttributeField(password)
    >>> field.raw_value
    'new_passwd'

    >>> field.set(required=True)
    AttributeField(password)
    >>> field.validators  #doctest: +ELLIPSIS
    [<function required at ...>]
    >>> field.set(required=False)
    AttributeField(password)
    >>> field.validators
    []

    >>> field.set(html={'this': 'that'})
    AttributeField(password)
    >>> field.html_options
    {'this': 'that'}
    >>> field.set(html={'some': 'thing'})
    AttributeField(password)
    >>> field.html_options
    {'this': 'that', 'some': 'thing'}

    >>> bob = lambda x: x
    >>> field.set(validators=[bob])
    AttributeField(password)
    >>> field.validators  #doctest: +ELLIPSIS
    [<function <lambda> at ...>]

    >>> field.set(validators=[bob])
    AttributeField(password)
    >>> field.validators  #doctest: +ELLIPSIS
    [<function <lambda> at ...>, <function <lambda> at ...>]

    >>> field.set(non_exist=True)
    Traceback (most recent call last):
    ...
    ValueError: Invalid argument non_exist

    """

