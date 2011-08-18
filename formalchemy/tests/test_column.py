# -*- coding: utf-8 -*-
from formalchemy.tests import *

class Label(Base):
    __tablename__ = 'label'
    id = Column(Integer, primary_key=True)
    label = Column(String, label='My label')

def test_label():
    """
    >>> Label.__table__.c.label.info
    {'label': 'My label'}
    >>> fs = FieldSet(Label)
    >>> print fs.label.label_text
    My label
    >>> print fs.label.label()
    My label
    """

def test_fk_label(self):
    """
    >>> fs = FieldSet(Order)
    >>> print fs.user.label_text
    User
    >>> print fs.user.label()
    User
    """

