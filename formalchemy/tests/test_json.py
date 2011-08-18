# -*- coding: utf-8 -*-
from formalchemy.tests import *
from formalchemy.fields import PasswordFieldRenderer
try:
    import json
except ImportError:
    import simplejson as json

def to_dict():
    """
    >>> fs = FieldSet(User, session=session)
    >>> _ = fs.password.set(renderer=PasswordFieldRenderer)

    >>> fs.to_dict()
    {u'User--id': None, u'User--name': None, u'User--email': None, u'User--orders': []}

    >>> fs = FieldSet(bill)
    >>> _ = fs.password.set(renderer=PasswordFieldRenderer)

    >>> fs.to_dict()
    {u'User-1-email': u'bill@example.com', u'User-1-id': 1, u'User-1-orders': [1], u'User-1-name': u'Bill'}

    >>> fs.to_dict(with_prefix=False)
    {'orders': [1], 'id': 1, 'name': u'Bill', 'email': u'bill@example.com'}

    >>> print json.dumps(fs.to_dict(with_prefix=False, as_string=True))
    {"orders": "Quantity: 10", "password": "******", "id": "1", "name": "Bill", "email": "bill@example.com"}
    """

def bind_without_prefix():
    """
    >>> data = {u'password': u'1', u'id': 1, u'orders': [1], u'email': u'bill@example.com', u'name': u'Bill'}

    >>> fs = FieldSet(User)
    >>> fs = fs.bind(data=data, session=session, with_prefix=False)
    >>> fs.validate()
    True

    >>> fs.rebind(bill, data=data, with_prefix=False)
    >>> fs.validate()
    True
    >>> fs.password.value
    u'1'

    >>> data = {u'password': u'2', u'id': 1, u'orders': [1], u'email': u'bill@example.com', u'name': u'Bill'}
    >>> fs = fs.bind(bill, data=data, with_prefix=False)
    >>> fs.validate()
    True
    >>> fs.password.value
    u'2'

    """
