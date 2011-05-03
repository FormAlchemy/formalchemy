from formalchemy.tests import *
from formalchemy.fields import DateTimeFieldRenderer
import datetime


class Dt(Base):
    __tablename__ = 'dts'
    id = Column('id', Integer, primary_key=True)
    foo = Column('foo', Date, nullable=True)
    bar = Column('bar', Time, nullable=True)
    foobar = Column('foobar', DateTime, nullable=True)

class DateTimeFieldRendererFr(DateTimeFieldRenderer):
    edit_format = 'd-m-y'

def test_dt_hang_up():
    """
    >>> class MyClass(object):
    ...     td = Field(type=types.DateTime, value=datetime.datetime.now())
    ...     t = Field().required()
    >>> MyFS = FieldSet(MyClass)

    >>> fs = MyFS.bind(model=MyClass, data={
    ...     'MyClass--td__year': '2011',
    ...     'MyClass--td__month': '12',
    ...     'MyClass--td__day': '12',
    ...     'MyClass--td__hour': '17',
    ...     'MyClass--td__minute': '28',
    ...     'MyClass--td__second': '49',
    ...     'MyClass--t': ""})

    >>> fs.validate()
    False

    >>> print pretty_html(fs.td.render()) #doctest: +ELLIPSIS
    <span id="MyClass--td">
     <select id="MyClass--td__month" name="MyClass--td__month">
      ...
      <option selected="selected" value="12">
       December
      </option>
     </select>
     <select id="MyClass--td__day" name="MyClass--td__day">
      <option value="DD">
       Day
      </option>
      ...
      <option selected="selected" value="12">
       12
      </option>
      ...
     </select>
     <input id="MyClass--td__year" maxlength="4" name="MyClass--td__year" size="4" type="text" value="2011" />
     <select id="MyClass--td__hour" name="MyClass--td__hour">
      <option value="HH">
       HH
      </option>
      ...
      <option selected="selected" value="17">
       17
      </option>
      ...
     </select>
     :
     <select id="MyClass--td__minute" name="MyClass--td__minute">
      <option value="MM">
       MM
      </option>
      ...
      <option selected="selected" value="28">
       28
      </option>
      ...
     </select>
     :
     <select id="MyClass--td__second" name="MyClass--td__second">
      <option value="SS">
       SS
      </option>
      ...
      <option selected="selected" value="49">
       49
      </option>
      ...
     </select>
    </span>

    >>> fs.td.value
    datetime.datetime(2011, 12, 12, 17, 28, 49)
    """

def test_hidden():
    """
    >>> fs = FieldSet(Dt)
    >>> _ = fs.foo.set(hidden=True)
    >>> print pretty_html(fs.foo.render()) #doctest: +ELLIPSIS
    <div style="display:none;">
     <span id="Dt--foo">
    ...

    >>> _ = fs.bar.set(hidden=True)
    >>> print pretty_html(fs.bar.render()) #doctest: +ELLIPSIS
    <div style="display:none;">
     <span id="Dt--bar">
    ...

    >>> _ = fs.foobar.set(hidden=True)
    >>> print pretty_html(fs.foobar.render()) #doctest: +ELLIPSIS
    <div style="display:none;">
     <span id="Dt--foobar">
    ...
    """



__doc__ = r"""
>>> fs = FieldSet(Dt)
>>> fs.configure(options=[fs.foobar.with_renderer(DateTimeFieldRendererFr)])
>>> print pretty_html(fs.foobar.with_html(lang='fr').render()) #doctest: +ELLIPSIS
<span id="Dt--foobar">
 <select id="Dt--foobar__day" lang="fr" name="Dt--foobar__day">
  <option selected="selected" value="DD">
   Jour
  </option>
...
 <select id="Dt--foobar__month" lang="fr" name="Dt--foobar__month">
  <option selected="selected" value="MM">
   Mois
  </option>
  <option value="1">
   Janvier
  </option>
...

>>> fs = FieldSet(Dt)
>>> print pretty_html(fs.foobar.render()) #doctest: +ELLIPSIS
<span id="Dt--foobar">
 <select id="Dt--foobar__month" name="Dt--foobar__month">
  <option selected="selected" value="MM">
   Month
  </option>
  ...
 </select>
 <select id="Dt--foobar__day" name="Dt--foobar__day">
  <option selected="selected" value="DD">
   Day
  </option>
  ...
 </select>
 <input id="Dt--foobar__year" maxlength="4" name="Dt--foobar__year" size="4" type="text" value="YYYY" />
 <select id="Dt--foobar__hour" name="Dt--foobar__hour">
  <option selected="selected" value="HH">
   HH
  </option>
  ...
 </select>
 :
 <select id="Dt--foobar__minute" name="Dt--foobar__minute">
  <option selected="selected" value="MM">
   MM
  </option>
  ...
 </select>
 :
 <select id="Dt--foobar__second" name="Dt--foobar__second">
  <option selected="selected" value="SS">
   SS
  </option>
  ...
 </select>
</span>

>>> fs = FieldSet(Dt)
>>> dt = fs.model
>>> dt.foo = datetime.date(2008, 6, 3);  dt.bar=datetime.time(14, 16, 18);  dt.foobar=datetime.datetime(2008, 6, 3, 14, 16, 18)
>>> print pretty_html(fs.foo.render()) #doctest: +ELLIPSIS
<span id="Dt--foo">
 <select id="Dt--foo__month" name="Dt--foo__month">
  <option value="MM">
   Month
  </option>
  ...
  <option selected="selected" value="6">
   June
  </option>
  ...
 </select>
 <select id="Dt--foo__day" name="Dt--foo__day">
  <option value="DD">
   Day
  </option>
  ...
  <option selected="selected" value="3">
   3
  </option>
  ...
  <option value="31">
   31
  </option>
 </select>
 <input id="Dt--foo__year" maxlength="4" name="Dt--foo__year" size="4" type="text" value="2008" />
</span>

>>> print pretty_html(fs.bar.render()) #doctest: +ELLIPSIS
<span id="Dt--bar">
 <select id="Dt--bar__hour" name="Dt--bar__hour">
  <option value="HH">
   HH
  </option>
  <option value="0">
   0
  </option>
  ...
  <option value="13">
   13
  </option>
  <option selected="selected" value="14">
   14
  </option>
  ...
  <option value="23">
   23
  </option>
 </select>
 :
 <select id="Dt--bar__minute" name="Dt--bar__minute">
  <option value="MM">
   MM
  </option>
  <option value="0">
   0
  </option>
  ...
  <option value="15">
   15
  </option>
  <option selected="selected" value="16">
   16
  </option>
  <option value="17">
   17
  </option>
  ...
  <option value="59">
   59
  </option>
 </select>
 :
 <select id="Dt--bar__second" name="Dt--bar__second">
  <option value="SS">
   SS
  </option>
  <option value="0">
   0
  </option>
  ...
  <option value="17">
   17
  </option>
  <option selected="selected" value="18">
   18
  </option>
  <option value="19">
   19
  </option>
  ...
  <option value="59">
   59
  </option>
 </select>
</span>

>>> print pretty_html(fs.foobar.render()) #doctest: +ELLIPSIS
<span id="Dt--foobar">
 <select id="Dt--foobar__month" name="Dt--foobar__month">
  <option value="MM">
   Month
  </option>
  ...
  <option selected="selected" value="6">
   June
  </option>
  ...
 </select>
 <select id="Dt--foobar__day" name="Dt--foobar__day">
  <option value="DD">
   Day
  </option>
  ...
  <option selected="selected" value="3">
   3
  </option>
  ...
 </select>
 <input id="Dt--foobar__year" maxlength="4" name="Dt--foobar__year" size="4" type="text" value="2008" />
 <select id="Dt--foobar__hour" name="Dt--foobar__hour">
  <option value="HH">
   HH
  </option>
  ...
  <option selected="selected" value="14">
   14
  </option>
  ...
 </select>
 :
 <select id="Dt--foobar__minute" name="Dt--foobar__minute">
  <option value="MM">
   MM
  </option>
  ...
  <option selected="selected" value="16">
   16
  </option>
  ...
 </select>
 :
 <select id="Dt--foobar__second" name="Dt--foobar__second">
  <option value="SS">
   SS
  </option>
  ...
  <option selected="selected" value="18">
   18
  </option>
  ...
 </select>
</span>

>>> fs.rebind(dt, data={'Dt--foo__day': 'DD', 'Dt--foo__month': '2', 'Dt--foo__year': '', 'Dt--bar__hour': 'HH', 'Dt--bar__minute': '6', 'Dt--bar__second': '8'})
>>> print pretty_html(fs.foo.render()) #doctest: +ELLIPSIS
<span id="Dt--foo">
 <select id="Dt--foo__month" name="Dt--foo__month">
  <option value="MM">
   Month
  </option>
  <option value="1">
   January
  </option>
  <option selected="selected" value="2">
   February
  </option>
  ...
 </select>
 <select id="Dt--foo__day" name="Dt--foo__day">
  <option value="DD">
   Day
  </option>
  <option value="1">
   1
  </option>
  ...
  <option value="31">
   31
  </option>
 </select>
 <input id="Dt--foo__year" maxlength="4" name="Dt--foo__year" size="4" type="text" value="" />
</span>
>>> print pretty_html(fs.bar.render()) #doctest: +ELLIPSIS
<span id="Dt--bar">
 <select id="Dt--bar__hour" name="Dt--bar__hour">
  <option value="HH">
   HH
  </option>
  ...
  <option selected="selected" value="14">
   14
  </option>
  ...
 </select>
 :
 <select id="Dt--bar__minute" name="Dt--bar__minute">
  <option value="MM">
   MM
  </option>
  ...
  <option selected="selected" value="6">
   6
  </option>
  ...
 </select>
 :
 <select id="Dt--bar__second" name="Dt--bar__second">
  <option value="SS">
   SS
  </option>
  ...
  <option selected="selected" value="8">
   8
  </option>
  ...
 </select>
</span>

>>> fs.rebind(dt, data={'Dt--foo__day': '11', 'Dt--foo__month': '2', 'Dt--foo__year': '1951', 'Dt--bar__hour': '4', 'Dt--bar__minute': '6', 'Dt--bar__second': '8', 'Dt--foobar__day': '11', 'Dt--foobar__month': '2', 'Dt--foobar__year': '1951', 'Dt--foobar__hour': '4', 'Dt--foobar__minute': '6', 'Dt--foobar__second': '8'})
>>> fs.sync()
>>> dt.foo
datetime.date(1951, 2, 11)
>>> dt.bar
datetime.time(4, 6, 8)
>>> dt.foobar
datetime.datetime(1951, 2, 11, 4, 6, 8)
>>> session.rollback()

>>> fs.rebind(dt, data={'Dt--foo__day': 'DD', 'Dt--foo__month': 'MM', 'Dt--foo__year': 'YYYY', 'Dt--bar__hour': 'HH', 'Dt--bar__minute': 'MM', 'Dt--bar__second': 'SS', 'Dt--foobar__day': 'DD', 'Dt--foobar__month': 'MM', 'Dt--foobar__year': '', 'Dt--foobar__hour': 'HH', 'Dt--foobar__minute': 'MM', 'Dt--foobar__second': 'SS'})
>>> fs.validate()
True
>>> fs.sync()
>>> dt.foo is None
True
>>> dt.bar is None
True
>>> dt.foobar is None
True
>>> session.rollback()

>>> fs.rebind(dt, data={'Dt--foo__day': '1', 'Dt--foo__month': 'MM', 'Dt--foo__year': 'YYYY', 'Dt--bar__hour': 'HH', 'Dt--bar__minute': 'MM', 'Dt--bar__second': 'SS', 'Dt--foobar__day': 'DD', 'Dt--foobar__month': 'MM', 'Dt--foobar__year': '', 'Dt--foobar__hour': 'HH', 'Dt--foobar__minute': 'MM', 'Dt--foobar__second': 'SS'})
>>> fs.validate()
False
>>> fs.errors
{AttributeField(foo): ['Invalid date']}

>>> fs.rebind(dt, data={'Dt--foo__day': 'DD', 'Dt--foo__month': 'MM', 'Dt--foo__year': 'YYYY', 'Dt--bar__hour': 'HH', 'Dt--bar__minute': '1', 'Dt--bar__second': 'SS', 'Dt--foobar__day': 'DD', 'Dt--foobar__month': 'MM', 'Dt--foobar__year': '', 'Dt--foobar__hour': 'HH', 'Dt--foobar__minute': 'MM', 'Dt--foobar__second': 'SS'})
>>> fs.validate()
False
>>> fs.errors
{AttributeField(bar): ['Invalid time']}

>>> fs.rebind(dt, data={'Dt--foo__day': 'DD', 'Dt--foo__month': 'MM', 'Dt--foo__year': 'YYYY', 'Dt--bar__hour': 'HH', 'Dt--bar__minute': 'MM', 'Dt--bar__second': 'SS', 'Dt--foobar__day': '11', 'Dt--foobar__month': '2', 'Dt--foobar__year': '1951', 'Dt--foobar__hour': 'HH', 'Dt--foobar__minute': 'MM', 'Dt--foobar__second': 'SS'})
>>> fs.validate()
False
>>> fs.errors
{AttributeField(foobar): ['Incomplete datetime']}

>>> fs.rebind(dt)
>>> dt.bar = datetime.time(0)
>>> print fs.bar.render() #doctest: +ELLIPSIS
<span id="Dt--bar"><select id="Dt--bar__hour" name="Dt--bar__hour">
<option value="HH">HH</option>
<option selected="selected" value="0">0</option>
...

>>> print fs.bar.render_readonly()
00:00:00

>>> fs = FieldSet(Dt)
>>> print fs.bar.render() #doctest: +ELLIPSIS
<span id="Dt--bar"><select id="Dt--bar__hour" name="Dt--bar__hour">
<option selected="selected" value="HH">HH</option>
<option value="0">0</option>
...

"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()
