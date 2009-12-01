# -*- coding: utf-8 -*-
from formalchemy.tests import *

def test_dropdown():
    """
    >>> fs = FieldSet(bill)
    >>> print pretty_html(fs.orders.render())
    <select id="User-1-orders" multiple="multiple" name="User-1-orders" size="5">
     <option value="2">
      Quantity: 5
     </option>
     <option value="3">
      Quantity: 6
     </option>
     <option selected="selected" value="1">
      Quantity: 10
     </option>
    </select>
    """

def test_lazy_filtered_dropdown():
    """
    >>> fs = FieldSet(bill)
    >>> def available_orders(fs_):
    ...     return fs_.session.query(Order).filter_by(quantity=10)
    >>> fs.configure(include=[fs.orders.dropdown(options=available_orders)])
    >>> print pretty_html(fs.orders.render())
    <select id="User-1-orders" multiple="multiple" name="User-1-orders" size="5">
     <option selected="selected" value="1">
      Quantity: 10
     </option>
    </select>
    """

def test_lazy_record():
    """
    >>> fs = FieldSet(bill)
    >>> r = engine.execute('select quantity, user_id from orders').fetchall()
    >>> r = engine.execute("select 'Swedish' as name, 'sv_SE' as iso_code union all select 'English', 'en_US'").fetchall()
    >>> fs.configure(include=[fs.orders.dropdown(options=r)])
    >>> print pretty_html(fs.orders.render())
    <select id="User-1-orders" multiple="multiple" name="User-1-orders" size="5">
     <option value="sv_SE">
      Swedish
     </option>
     <option value="en_US">
      English
     </option>
    </select>
    """
