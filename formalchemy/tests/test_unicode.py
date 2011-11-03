# -*- coding: utf-8 -*-
from formalchemy.tests import *
from formalchemy.multidict import UnicodeMultiDict
from formalchemy.multidict import MultiDict

def test_unicode():
    """
    >>> jose = User(email='jose@example.com',
    ...             password='6565',
    ...             name=u'Jos\xe9')
    >>> order4 = Order(user=jose, quantity=4)
    >>> session.add(jose)
    >>> session.add(order4)
    >>> session.flush()
    >>> FieldSet.default_renderers = original_renderers.copy()
    >>> fs = FieldSet(jose)
    >>> print fs.render() #doctest: +ELLIPSIS
    <div>
    ...<input id="User-3-name" maxlength="30" name="User-3-name" type="text" value="José" />...

    >>> fs.readonly = True
    >>> print fs.render() #doctest: +ELLIPSIS
    <tbody>...José...

    >>> fs = FieldSet(order4)
    >>> print fs.render() #doctest: +ELLIPSIS
    <div>
    ...José...

    >>> fs.readonly = True
    >>> print fs.render() #doctest: +ELLIPSIS
    <tbody>...José...

    >>> session.rollback()
    """

def test_unicode_data(self):
    """
    >>> fs = FieldSet(User, session=session)
    >>> data = UnicodeMultiDict(MultiDict({'User--name': 'José', 'User--email': 'j@jose.com', 'User--password': 'pwd'}), encoding='utf-8')
    >>> data.encoding
    'utf-8'
    >>> fs.rebind(data=data)
    >>> fs.data is data
    True
    >>> print(fs.render()) # doctest: +ELLIPSIS
    <div>...<input id="User--name" maxlength="30" name="User--name" type="text" value="José" />...</div>

    >>> data = UnicodeMultiDict(MultiDict({'name': 'José', 'email': 'j@jose.com', 'password': 'pwd'}), encoding='utf-8')
    >>> fs.rebind(data=data, with_prefix=False)
    >>> print(fs.render()) # doctest: +ELLIPSIS
    <div>...<input id="User--name" maxlength="30" name="User--name" type="text" value="José" />...</div>

    >>> fs.rebind(data={'User--name': 'José', 'User--email': 'j@jose.com', 'User--password': 'pwd'})
    >>> isinstance(fs.data, UnicodeMultiDict)
    True
    >>> print(fs.render()) # doctest: +ELLIPSIS
    <div>...<input id="User--name" maxlength="30" name="User--name" type="text" value="José" />...</div>
    """
