# Copyright (C) 2007 Alexandre Conrad, alexandre (dot) conrad (at) gmail (dot) com
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy import Column as SAColumn
from formalchemy import templates
from formalchemy import config
from formalchemy.tables import *
from formalchemy.forms import *
from formalchemy.fields import *
from formalchemy.validators import ValidationError
import formalchemy.validators as validators
import formalchemy.fatypes as types

column_options = Field._valide_options[:]
column_options.extend(['backref_%s' % v for v in Field._valide_options])

def Column(*args, **kwargs):
    """Wrap the standard Column to allow to add some FormAlchemy options to a
    model field. Basically label and renderer but all the values are passed to
    :meth:`~formalchemy.fields.AbstractField.set`::

        >>> from sqlalchemy import Integer
        >>> from sqlalchemy.ext.declarative import declarative_base
        >>> from formalchemy import Column
        >>> Base = declarative_base()
        >>> class MyArticle(Base):
        ...     __tablename__ = 'myarticles'
        ...     id = Column(Integer, primary_key=True, label='My id')
        >>> MyArticle.__table__.c.id.info
        {'label': 'My id'}

    """
    info = kwargs.get('info', {})
    for k, v in kwargs.items():
        if k in column_options:
            info[k] = kwargs.pop(k)
    if info:
        kwargs['info'] = info
    return SAColumn(*args, **kwargs)


__all__ = ["FieldSet", "Field", "FieldRenderer", "Grid", "ValidationError", "validators", "SimpleMultiDict", "types"]
__version__ = "1.4.2"

