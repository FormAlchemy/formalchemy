# -*- coding: utf-8 -*-
from formalchemy.tests import *


def test_aliases():
    fs = FieldSet(Aliases)
    fs.bind(Aliases)
    assert fs.id.name == 'row_id'
    assert fs.id.attribute_name == 'id'

def test_render_aliases(self):
    """
    >>> alias = session.query(Aliases).first()
    >>> alias
    >>> fs = FieldSet(Aliases)
    >>> print fs.render()
    <div>
     <label class="field_opt" for="Aliases--row_text">
      Text
     </label>
     <input id="Aliases--row_text" name="Aliases--row_text" type="text" />
    </div>
    <script type="text/javascript">
     //<![CDATA[
    document.getElementById("Aliases--row_text").focus();
    //]]>
    </script>
    """

