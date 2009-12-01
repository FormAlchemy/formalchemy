# -*- coding: utf-8 -*-
from formalchemy.tests import *

def test_renderer_names():
    """
    Check that the input name take care of multiple primary keys::

        >>> fs = FieldSet(primary1)
        >>> print fs.field.render()
        <input id="PrimaryKeys-1_22-field" maxlength="10" name="PrimaryKeys-1_22-field" type="text" value="value1" />

        >>> fs = FieldSet(primary2)
        >>> print fs.field.render()
        <input id="PrimaryKeys-1_33-field" maxlength="10" name="PrimaryKeys-1_33-field" type="text" value="value2" />

    Check form rendering with keys::

        >>> fs = FieldSet(primary2)
        >>> fs.configure(pk=True)
        >>> print fs.render()
        <div>
         <label class="field_req" for="PrimaryKeys-1_33-id">
          Id
         </label>
         <input id="PrimaryKeys-1_33-id" name="PrimaryKeys-1_33-id" type="text" value="1" />
        </div>
        <script type="text/javascript">
         //<![CDATA[
        document.getElementById("PrimaryKeys-1_33-id").focus();
        //]]>
        </script>
        <div>
         <label class="field_req" for="PrimaryKeys-1_33-id2">
          Id2
         </label>
         <input id="PrimaryKeys-1_33-id2" maxlength="10" name="PrimaryKeys-1_33-id2" type="text" value="33" />
        </div>
        <div>
         <label class="field_req" for="PrimaryKeys-1_33-field">
          Field
         </label>
         <input id="PrimaryKeys-1_33-field" maxlength="10" name="PrimaryKeys-1_33-field" type="text" value="value2" />
        </div>
    """

def test_foreign_keys():
    """
    Assume that we can have more than one ForeignKey as primary key::

        >>> fs = FieldSet(orderuser2)
        >>> fs.configure(pk=True)

        >>> print pretty_html(fs.user.render())
        <select id="OrderUser-1_2-user_id" name="OrderUser-1_2-user_id">
         <option selected="selected" value="1">
          Bill
         </option>
         <option value="2">
          John
         </option>
        </select>

        >>> print pretty_html(fs.order.render())
        <select id="OrderUser-1_2-order_id" name="OrderUser-1_2-order_id">
         <option value="1">
          Quantity: 10
         </option>
         <option selected="selected" value="2">
          Quantity: 5
         </option>
         <option value="3">
          Quantity: 6
         </option>
        </select>
    """


def test_deserialize():
    """
    Assume that we can deserialize a value
    """
    fs = FieldSet(primary1, data={'PrimaryKeys-1_22-field':'new_value'})
    assert fs.validate() is True
    assert fs.field.value == 'new_value'
    fs.sync()
    session.rollback()

def test_deserialize_new_record():
    """
    Assume that we can deserialize a value
    """
    fs = FieldSet(PrimaryKeys(), data={'PrimaryKeys-_-id':'8',
                                       'PrimaryKeys-_-id2':'9'})
    fs.configure(include=[fs.id, fs.id2])
    assert fs.validate() is True
    fs.sync()
    assert fs.model.id == 8, fs.model.id
    assert fs.model.id2 == '9', fs.model.id2
    session.rollback()


