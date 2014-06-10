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

    >>> sorted(str("%s=%s"%(k,v)) for k,v in fs.to_dict().items())
    ['User--email=None', 'User--id=None', 'User--name=None', 'User--orders=[]']

    >>> fs = FieldSet(bill)
    >>> _ = fs.password.set(renderer=PasswordFieldRenderer)

    >>> sorted(str("%s=%s"%(k,v)) for k,v in fs.to_dict().items())
    ['User-1-email=bill@example.com', 'User-1-id=1', 'User-1-name=Bill', 'User-1-orders=[1]']

    >>> sorted(str("%s=%s"%(k,v)) for k,v in fs.to_dict(with_prefix=False).items())
    ['email=bill@example.com', 'id=1', 'name=Bill', 'orders=[1]']

    Yes, this is convoluted; the order of keys in json.dumps() is undefined.

    >>> d = json.loads(json.dumps(fs.to_dict(with_prefix=False, as_string=True)))
    >>> sorted(str("%s=%s"%(k,v)) for k,v in d.items())
    ['email=bill@example.com', 'id=1', 'name=Bill', 'orders=Quantity: 10', 'password=******']
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
    '1'

    >>> data = {u'password': u'2', u'id': 1, u'orders': [1], u'email': u'bill@example.com', u'name': u'Bill'}
    >>> fs = fs.bind(bill, data=data, with_prefix=False)
    >>> fs.validate()
    True
    >>> fs.password.value
    '2'

    """
