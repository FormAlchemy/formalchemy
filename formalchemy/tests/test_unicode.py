# -*- coding: utf-8 -*-
__doc__ = r"""
>>> from formalchemy.tests import *

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


