# -*- coding: utf-8 -*-
__doc__ = r"""
>>> from formalchemy.tests import *

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
...Jos&#233;...

>>> fs.readonly = True
>>> print fs.render() #doctest: +ELLIPSIS
<tbody>...José...

"""


