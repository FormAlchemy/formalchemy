# -*- coding: utf-8 -*-
from formalchemy.tests import *
from webob import Request

def test_get():
    """
    >>> fs = FieldSet(User)
    >>> request = Request.blank('/')
    >>> fs = fs.bind(User, request=request)
    >>> fs.id.renderer.request is request
    True
    """

def test_post():
    """
    >>> fs = FieldSet(User)
    >>> request = Request.blank('/')
    >>> request.method = 'POST'
    >>> request.POST['User--id'] = '1'
    >>> request.POST['User--name'] = 'bill'
    >>> request.POST['User--email'] = 'a@a.com'
    >>> request.POST['User--password'] = 'xx'
    >>> fs = fs.bind(request=request)
    >>> fs.id.renderer.request is request
    True
    >>> fs.validate()
    True
    """

