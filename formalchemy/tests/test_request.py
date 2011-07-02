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

def test_post_on_fieldset():
    """
    >>> request = Request.blank('/')
    >>> request.method = 'POST'
    >>> request.POST['User--id'] = '1'
    >>> request.POST['User--name'] = 'bill'
    >>> request.POST['User--email'] = 'a@a.com'
    >>> request.POST['User--password'] = 'xx'
    >>> fs = FieldSet(User, request=request)
    >>> fs.id.renderer.request is request
    True
    >>> fs.validate()
    True
    """
    
def test_post_on_grid():
    """
    >>> request = Request.blank('/')
    >>> request.method = 'POST'
    >>> request.POST['User-1-id'] = '1'
    >>> request.POST['User-1-name'] = 'bill'
    >>> request.POST['User-1-email'] = 'a@a.com'
    >>> request.POST['User-1-password'] = 'xx'
    >>> g = Grid(User, [bill], request=request)
    >>> g.id.renderer.request is request
    True
    >>> g.validate()
    True
    >>> print g.render()  #doctest: +ELLIPSIS
    <thead>...<input id="User-1-password" maxlength="20" name="User-1-password" type="text" value="xx" />...</tbody>
    """
    

