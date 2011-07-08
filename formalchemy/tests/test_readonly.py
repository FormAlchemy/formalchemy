# -*- coding: utf-8 -*-
from formalchemy.tests import *


def test_readonly_mode():
    """
    Assume that the field value is render in readonly mode::

        >>> fs = FieldSet(Two)
        >>> fs.configure(options=[fs.foo.readonly()])
        >>> print fs.render()
        <div>
         <label class="field_opt" for="Two--foo">
          Foo
         </label>
         133
        </div>
    """

def test_focus_with_readonly_mode():
    """
    Assume that the field value is render in readonly mode and that the focus
    is set to the correct field::

        >>> fs = FieldSet(Three)
        >>> fs.configure(options=[fs.foo.readonly()])
        >>> print fs.render()
        <div>
         <label class="field_opt" for="Three--foo">
          Foo
         </label>
        </div>
        <div>
         <label class="field_opt" for="Three--bar">
          Bar
         </label>
         <input id="Three--bar" name="Three--bar" type="text" />
        </div>
        <script type="text/javascript">
         //<![CDATA[
        document.getElementById("Three--bar").focus();
        //]]>
        </script>

    """

def test_ignore_request_in_readonly():
    fs = FieldSet(bill)

    value = bill.name

    assert fs.name.value == value, '%s != %s' % (fs.name.value, value)

    fs.configure(options=[fs.name.readonly()])

    assert value in fs.render(), fs.render()

    data = {'User-1-password':bill.password,
            'User-1-email': bill.email,
            'User-1-name': 'new name',
            'User-1-orders': [o.id for o in bill.orders]}

    fs.rebind(bill, data=data)
    fs.configure(options=[fs.name.readonly()])

    assert fs.name.value == value, '%s != %s' % (fs.name.value, value)

    assert fs.name.is_readonly()

    fs.sync()

    assert bill.name == value, '%s != %s' % (bill.name, value)

    bill.name = value



