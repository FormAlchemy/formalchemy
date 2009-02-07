# -*- coding: utf-8 -*-
from formalchemy.tests import *


def test_aliases():
    fs = FieldSet(Aliases)
    fs.bind(Aliases)
    assert fs.id.name == 'id'

def test_render_aliases():
    """
    >>> alias = session.query(Aliases).first()
    >>> alias
    >>> fs = FieldSet(Aliases)
    >>> print fs.render()
    <div>
     <label class="field_opt" for="Aliases--text">
      Text
     </label>
     <input id="Aliases--text" name="Aliases--text" type="text" />
    </div>
    <script type="text/javascript">
     //<![CDATA[
    document.getElementById("Aliases--text").focus();
    //]]>
    </script>
    """

