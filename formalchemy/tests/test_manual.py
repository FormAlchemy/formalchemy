# -*- coding: utf-8 -*-
from formalchemy.tests import FieldSet, Field, EscapingReadonlyRenderer, types, configure_and_render, pretty_html

class Manual(object):
    a = Field()
    b = Field(type=types.Integer).dropdown([('one', 1), ('two', 2)], multiple=True)
    d = Field().textarea((80, 10))

class ReportByUserForm(object):
   user_id = Field(type=types.Integer)
   from_date = Field(type=types.Date).required()
   to_date = Field(type=types.Date).required()


def test_manual(self):
    """
    >>> fs = FieldSet(Manual)
    >>> print configure_and_render(fs, focus=None)
    <div>
     <label class="field_opt" for="Manual--a">
      A
     </label>
     <input id="Manual--a" name="Manual--a" type="text" />
    </div>
    <div>
     <label class="field_opt" for="Manual--b">
      B
     </label>
     <select id="Manual--b" multiple="multiple" name="Manual--b" size="5">
      <option value="1">
       one
      </option>
      <option value="2">
       two
      </option>
     </select>
    </div>
    <div>
     <label class="field_opt" for="Manual--d">
      D
     </label>
     <textarea cols="80" id="Manual--d" name="Manual--d" rows="10">
     </textarea>
    </div>
    >>> fs.rebind(data={'Manual--a': 'asdf'})
    >>> print pretty_html(fs.a.render())
    <input id="Manual--a" name="Manual--a" type="text" value="asdf" />

    >>> t = FieldSet(Manual)
    >>> t.configure(include=[t.a, t.b], readonly=True)
    >>> t.model.b = [1, 2]
    >>> print t.render()
    <tbody>
     <tr>
      <td class="field_readonly">
       A:
      </td>
      <td>
      </td>
     </tr>
     <tr>
      <td class="field_readonly">
       B:
      </td>
      <td>
       one, two
      </td>
     </tr>
    </tbody>
    >>> t.model.a = 'test'
    >>> print t.a.render_readonly()
    test
    >>> t.configure(readonly=True, options=[t.a.with_renderer(EscapingReadonlyRenderer)])
    >>> t.model.a = '<test>'
    >>> print t.a.render_readonly()
    &lt;test&gt;

    """

def test_manual2():
    """
    >>> fs = FieldSet(ReportByUserForm)
    >>> print fs.render() #doctest: +ELLIPSIS
    <div>
     <label class="field_req" for="ReportByUserForm--from_date">
      From date
     </label>
    ...
    <div>
     <label class="field_opt" for="ReportByUserForm--user_id">
      User id
     </label>
     <input id="ReportByUserForm--user_id" name="ReportByUserForm--user_id" type="text" />
    </div>
    """
