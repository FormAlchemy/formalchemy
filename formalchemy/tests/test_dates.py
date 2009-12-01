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

__doc__ = r"""
>>> fs = FieldSet(Dt)
>>> fs.configure(options=[fs.foobar.with_renderer(DateTimeFieldRendererFr)])
>>> print pretty_html(fs.foobar.with_html(lang='fr').render()) #doctest: +ELLIPSIS
<span id="Dt--foobar">
 <select id="Dt--foobar__day" lang="fr" name="Dt--foobar__day">
  <option value="DD">
   Jour
  </option>
...
 <select id="Dt--foobar__month" lang="fr" name="Dt--foobar__month">
  <option value="MM">
   Mois
  </option>
  <option value="1">
   Janvier
  </option>
...

>>> fs = FieldSet(Dt)
>>> print pretty_html(fs.foobar.render())
<span id="Dt--foobar">
 <select id="Dt--foobar__month" name="Dt--foobar__month">
  <option value="MM">
   Month
  </option>
  <option value="1">
   January
  </option>
  <option value="2">
   February
  </option>
  <option value="3">
   March
  </option>
  <option value="4">
   April
  </option>
  <option value="5">
   May
  </option>
  <option value="6">
   June
  </option>
  <option value="7">
   July
  </option>
  <option value="8">
   August
  </option>
  <option value="9">
   September
  </option>
  <option value="10">
   October
  </option>
  <option value="11">
   November
  </option>
  <option value="12">
   December
  </option>
 </select>
 <select id="Dt--foobar__day" name="Dt--foobar__day">
  <option value="DD">
   Day
  </option>
  <option value="1">
   1
  </option>
  <option value="2">
   2
  </option>
  <option value="3">
   3
  </option>
  <option value="4">
   4
  </option>
  <option value="5">
   5
  </option>
  <option value="6">
   6
  </option>
  <option value="7">
   7
  </option>
  <option value="8">
   8
  </option>
  <option value="9">
   9
  </option>
  <option value="10">
   10
  </option>
  <option value="11">
   11
  </option>
  <option value="12">
   12
  </option>
  <option value="13">
   13
  </option>
  <option value="14">
   14
  </option>
  <option value="15">
   15
  </option>
  <option value="16">
   16
  </option>
  <option value="17">
   17
  </option>
  <option value="18">
   18
  </option>
  <option value="19">
   19
  </option>
  <option value="20">
   20
  </option>
  <option value="21">
   21
  </option>
  <option value="22">
   22
  </option>
  <option value="23">
   23
  </option>
  <option value="24">
   24
  </option>
  <option value="25">
   25
  </option>
  <option value="26">
   26
  </option>
  <option value="27">
   27
  </option>
  <option value="28">
   28
  </option>
  <option value="29">
   29
  </option>
  <option value="30">
   30
  </option>
  <option value="31">
   31
  </option>
 </select>
 <input id="Dt--foobar__year" maxlength="4" name="Dt--foobar__year" size="4" type="text" value="YYYY" />
 <select id="Dt--foobar__hour" name="Dt--foobar__hour">
  <option value="HH">
   HH
  </option>
  <option value="0">
   0
  </option>
  <option value="1">
   1
  </option>
  <option value="2">
   2
  </option>
  <option value="3">
   3
  </option>
  <option value="4">
   4
  </option>
  <option value="5">
   5
  </option>
  <option value="6">
   6
  </option>
  <option value="7">
   7
  </option>
  <option value="8">
   8
  </option>
  <option value="9">
   9
  </option>
  <option value="10">
   10
  </option>
  <option value="11">
   11
  </option>
  <option value="12">
   12
  </option>
  <option value="13">
   13
  </option>
  <option value="14">
   14
  </option>
  <option value="15">
   15
  </option>
  <option value="16">
   16
  </option>
  <option value="17">
   17
  </option>
  <option value="18">
   18
  </option>
  <option value="19">
   19
  </option>
  <option value="20">
   20
  </option>
  <option value="21">
   21
  </option>
  <option value="22">
   22
  </option>
  <option value="23">
   23
  </option>
 </select>
 :
 <select id="Dt--foobar__minute" name="Dt--foobar__minute">
  <option value="MM">
   MM
  </option>
  <option value="0">
   0
  </option>
  <option value="1">
   1
  </option>
  <option value="2">
   2
  </option>
  <option value="3">
   3
  </option>
  <option value="4">
   4
  </option>
  <option value="5">
   5
  </option>
  <option value="6">
   6
  </option>
  <option value="7">
   7
  </option>
  <option value="8">
   8
  </option>
  <option value="9">
   9
  </option>
  <option value="10">
   10
  </option>
  <option value="11">
   11
  </option>
  <option value="12">
   12
  </option>
  <option value="13">
   13
  </option>
  <option value="14">
   14
  </option>
  <option value="15">
   15
  </option>
  <option value="16">
   16
  </option>
  <option value="17">
   17
  </option>
  <option value="18">
   18
  </option>
  <option value="19">
   19
  </option>
  <option value="20">
   20
  </option>
  <option value="21">
   21
  </option>
  <option value="22">
   22
  </option>
  <option value="23">
   23
  </option>
  <option value="24">
   24
  </option>
  <option value="25">
   25
  </option>
  <option value="26">
   26
  </option>
  <option value="27">
   27
  </option>
  <option value="28">
   28
  </option>
  <option value="29">
   29
  </option>
  <option value="30">
   30
  </option>
  <option value="31">
   31
  </option>
  <option value="32">
   32
  </option>
  <option value="33">
   33
  </option>
  <option value="34">
   34
  </option>
  <option value="35">
   35
  </option>
  <option value="36">
   36
  </option>
  <option value="37">
   37
  </option>
  <option value="38">
   38
  </option>
  <option value="39">
   39
  </option>
  <option value="40">
   40
  </option>
  <option value="41">
   41
  </option>
  <option value="42">
   42
  </option>
  <option value="43">
   43
  </option>
  <option value="44">
   44
  </option>
  <option value="45">
   45
  </option>
  <option value="46">
   46
  </option>
  <option value="47">
   47
  </option>
  <option value="48">
   48
  </option>
  <option value="49">
   49
  </option>
  <option value="50">
   50
  </option>
  <option value="51">
   51
  </option>
  <option value="52">
   52
  </option>
  <option value="53">
   53
  </option>
  <option value="54">
   54
  </option>
  <option value="55">
   55
  </option>
  <option value="56">
   56
  </option>
  <option value="57">
   57
  </option>
  <option value="58">
   58
  </option>
  <option value="59">
   59
  </option>
 </select>
 :
 <select id="Dt--foobar__second" name="Dt--foobar__second">
  <option value="SS">
   SS
  </option>
  <option value="0">
   0
  </option>
  <option value="1">
   1
  </option>
  <option value="2">
   2
  </option>
  <option value="3">
   3
  </option>
  <option value="4">
   4
  </option>
  <option value="5">
   5
  </option>
  <option value="6">
   6
  </option>
  <option value="7">
   7
  </option>
  <option value="8">
   8
  </option>
  <option value="9">
   9
  </option>
  <option value="10">
   10
  </option>
  <option value="11">
   11
  </option>
  <option value="12">
   12
  </option>
  <option value="13">
   13
  </option>
  <option value="14">
   14
  </option>
  <option value="15">
   15
  </option>
  <option value="16">
   16
  </option>
  <option value="17">
   17
  </option>
  <option value="18">
   18
  </option>
  <option value="19">
   19
  </option>
  <option value="20">
   20
  </option>
  <option value="21">
   21
  </option>
  <option value="22">
   22
  </option>
  <option value="23">
   23
  </option>
  <option value="24">
   24
  </option>
  <option value="25">
   25
  </option>
  <option value="26">
   26
  </option>
  <option value="27">
   27
  </option>
  <option value="28">
   28
  </option>
  <option value="29">
   29
  </option>
  <option value="30">
   30
  </option>
  <option value="31">
   31
  </option>
  <option value="32">
   32
  </option>
  <option value="33">
   33
  </option>
  <option value="34">
   34
  </option>
  <option value="35">
   35
  </option>
  <option value="36">
   36
  </option>
  <option value="37">
   37
  </option>
  <option value="38">
   38
  </option>
  <option value="39">
   39
  </option>
  <option value="40">
   40
  </option>
  <option value="41">
   41
  </option>
  <option value="42">
   42
  </option>
  <option value="43">
   43
  </option>
  <option value="44">
   44
  </option>
  <option value="45">
   45
  </option>
  <option value="46">
   46
  </option>
  <option value="47">
   47
  </option>
  <option value="48">
   48
  </option>
  <option value="49">
   49
  </option>
  <option value="50">
   50
  </option>
  <option value="51">
   51
  </option>
  <option value="52">
   52
  </option>
  <option value="53">
   53
  </option>
  <option value="54">
   54
  </option>
  <option value="55">
   55
  </option>
  <option value="56">
   56
  </option>
  <option value="57">
   57
  </option>
  <option value="58">
   58
  </option>
  <option value="59">
   59
  </option>
 </select>
</span>

>>> fs = FieldSet(Dt)
>>> dt = fs.model
>>> dt.foo = datetime.date(2008, 6, 3);  dt.bar=datetime.time(14, 16, 18);  dt.foobar=datetime.datetime(2008, 6, 3, 14, 16, 18)
>>> print pretty_html(fs.foo.render())
<span id="Dt--foo">
 <select id="Dt--foo__month" name="Dt--foo__month">
  <option value="MM">
   Month
  </option>
  <option value="1">
   January
  </option>
  <option value="2">
   February
  </option>
  <option value="3">
   March
  </option>
  <option value="4">
   April
  </option>
  <option value="5">
   May
  </option>
  <option selected="selected" value="6">
   June
  </option>
  <option value="7">
   July
  </option>
  <option value="8">
   August
  </option>
  <option value="9">
   September
  </option>
  <option value="10">
   October
  </option>
  <option value="11">
   November
  </option>
  <option value="12">
   December
  </option>
 </select>
 <select id="Dt--foo__day" name="Dt--foo__day">
  <option value="DD">
   Day
  </option>
  <option value="1">
   1
  </option>
  <option value="2">
   2
  </option>
  <option selected="selected" value="3">
   3
  </option>
  <option value="4">
   4
  </option>
  <option value="5">
   5
  </option>
  <option value="6">
   6
  </option>
  <option value="7">
   7
  </option>
  <option value="8">
   8
  </option>
  <option value="9">
   9
  </option>
  <option value="10">
   10
  </option>
  <option value="11">
   11
  </option>
  <option value="12">
   12
  </option>
  <option value="13">
   13
  </option>
  <option value="14">
   14
  </option>
  <option value="15">
   15
  </option>
  <option value="16">
   16
  </option>
  <option value="17">
   17
  </option>
  <option value="18">
   18
  </option>
  <option value="19">
   19
  </option>
  <option value="20">
   20
  </option>
  <option value="21">
   21
  </option>
  <option value="22">
   22
  </option>
  <option value="23">
   23
  </option>
  <option value="24">
   24
  </option>
  <option value="25">
   25
  </option>
  <option value="26">
   26
  </option>
  <option value="27">
   27
  </option>
  <option value="28">
   28
  </option>
  <option value="29">
   29
  </option>
  <option value="30">
   30
  </option>
  <option value="31">
   31
  </option>
 </select>
 <input id="Dt--foo__year" maxlength="4" name="Dt--foo__year" size="4" type="text" value="2008" />
</span>

>>> print pretty_html(fs.bar.render())
<span id="Dt--bar">
 <select id="Dt--bar__hour" name="Dt--bar__hour">
  <option value="HH">
   HH
  </option>
  <option value="0">
   0
  </option>
  <option value="1">
   1
  </option>
  <option value="2">
   2
  </option>
  <option value="3">
   3
  </option>
  <option value="4">
   4
  </option>
  <option value="5">
   5
  </option>
  <option value="6">
   6
  </option>
  <option value="7">
   7
  </option>
  <option value="8">
   8
  </option>
  <option value="9">
   9
  </option>
  <option value="10">
   10
  </option>
  <option value="11">
   11
  </option>
  <option value="12">
   12
  </option>
  <option value="13">
   13
  </option>
  <option selected="selected" value="14">
   14
  </option>
  <option value="15">
   15
  </option>
  <option value="16">
   16
  </option>
  <option value="17">
   17
  </option>
  <option value="18">
   18
  </option>
  <option value="19">
   19
  </option>
  <option value="20">
   20
  </option>
  <option value="21">
   21
  </option>
  <option value="22">
   22
  </option>
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
  <option value="1">
   1
  </option>
  <option value="2">
   2
  </option>
  <option value="3">
   3
  </option>
  <option value="4">
   4
  </option>
  <option value="5">
   5
  </option>
  <option value="6">
   6
  </option>
  <option value="7">
   7
  </option>
  <option value="8">
   8
  </option>
  <option value="9">
   9
  </option>
  <option value="10">
   10
  </option>
  <option value="11">
   11
  </option>
  <option value="12">
   12
  </option>
  <option value="13">
   13
  </option>
  <option value="14">
   14
  </option>
  <option value="15">
   15
  </option>
  <option selected="selected" value="16">
   16
  </option>
  <option value="17">
   17
  </option>
  <option value="18">
   18
  </option>
  <option value="19">
   19
  </option>
  <option value="20">
   20
  </option>
  <option value="21">
   21
  </option>
  <option value="22">
   22
  </option>
  <option value="23">
   23
  </option>
  <option value="24">
   24
  </option>
  <option value="25">
   25
  </option>
  <option value="26">
   26
  </option>
  <option value="27">
   27
  </option>
  <option value="28">
   28
  </option>
  <option value="29">
   29
  </option>
  <option value="30">
   30
  </option>
  <option value="31">
   31
  </option>
  <option value="32">
   32
  </option>
  <option value="33">
   33
  </option>
  <option value="34">
   34
  </option>
  <option value="35">
   35
  </option>
  <option value="36">
   36
  </option>
  <option value="37">
   37
  </option>
  <option value="38">
   38
  </option>
  <option value="39">
   39
  </option>
  <option value="40">
   40
  </option>
  <option value="41">
   41
  </option>
  <option value="42">
   42
  </option>
  <option value="43">
   43
  </option>
  <option value="44">
   44
  </option>
  <option value="45">
   45
  </option>
  <option value="46">
   46
  </option>
  <option value="47">
   47
  </option>
  <option value="48">
   48
  </option>
  <option value="49">
   49
  </option>
  <option value="50">
   50
  </option>
  <option value="51">
   51
  </option>
  <option value="52">
   52
  </option>
  <option value="53">
   53
  </option>
  <option value="54">
   54
  </option>
  <option value="55">
   55
  </option>
  <option value="56">
   56
  </option>
  <option value="57">
   57
  </option>
  <option value="58">
   58
  </option>
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
  <option value="1">
   1
  </option>
  <option value="2">
   2
  </option>
  <option value="3">
   3
  </option>
  <option value="4">
   4
  </option>
  <option value="5">
   5
  </option>
  <option value="6">
   6
  </option>
  <option value="7">
   7
  </option>
  <option value="8">
   8
  </option>
  <option value="9">
   9
  </option>
  <option value="10">
   10
  </option>
  <option value="11">
   11
  </option>
  <option value="12">
   12
  </option>
  <option value="13">
   13
  </option>
  <option value="14">
   14
  </option>
  <option value="15">
   15
  </option>
  <option value="16">
   16
  </option>
  <option value="17">
   17
  </option>
  <option selected="selected" value="18">
   18
  </option>
  <option value="19">
   19
  </option>
  <option value="20">
   20
  </option>
  <option value="21">
   21
  </option>
  <option value="22">
   22
  </option>
  <option value="23">
   23
  </option>
  <option value="24">
   24
  </option>
  <option value="25">
   25
  </option>
  <option value="26">
   26
  </option>
  <option value="27">
   27
  </option>
  <option value="28">
   28
  </option>
  <option value="29">
   29
  </option>
  <option value="30">
   30
  </option>
  <option value="31">
   31
  </option>
  <option value="32">
   32
  </option>
  <option value="33">
   33
  </option>
  <option value="34">
   34
  </option>
  <option value="35">
   35
  </option>
  <option value="36">
   36
  </option>
  <option value="37">
   37
  </option>
  <option value="38">
   38
  </option>
  <option value="39">
   39
  </option>
  <option value="40">
   40
  </option>
  <option value="41">
   41
  </option>
  <option value="42">
   42
  </option>
  <option value="43">
   43
  </option>
  <option value="44">
   44
  </option>
  <option value="45">
   45
  </option>
  <option value="46">
   46
  </option>
  <option value="47">
   47
  </option>
  <option value="48">
   48
  </option>
  <option value="49">
   49
  </option>
  <option value="50">
   50
  </option>
  <option value="51">
   51
  </option>
  <option value="52">
   52
  </option>
  <option value="53">
   53
  </option>
  <option value="54">
   54
  </option>
  <option value="55">
   55
  </option>
  <option value="56">
   56
  </option>
  <option value="57">
   57
  </option>
  <option value="58">
   58
  </option>
  <option value="59">
   59
  </option>
 </select>
</span>

>>> print pretty_html(fs.foobar.render())
<span id="Dt--foobar">
 <select id="Dt--foobar__month" name="Dt--foobar__month">
  <option value="MM">
   Month
  </option>
  <option value="1">
   January
  </option>
  <option value="2">
   February
  </option>
  <option value="3">
   March
  </option>
  <option value="4">
   April
  </option>
  <option value="5">
   May
  </option>
  <option selected="selected" value="6">
   June
  </option>
  <option value="7">
   July
  </option>
  <option value="8">
   August
  </option>
  <option value="9">
   September
  </option>
  <option value="10">
   October
  </option>
  <option value="11">
   November
  </option>
  <option value="12">
   December
  </option>
 </select>
 <select id="Dt--foobar__day" name="Dt--foobar__day">
  <option value="DD">
   Day
  </option>
  <option value="1">
   1
  </option>
  <option value="2">
   2
  </option>
  <option selected="selected" value="3">
   3
  </option>
  <option value="4">
   4
  </option>
  <option value="5">
   5
  </option>
  <option value="6">
   6
  </option>
  <option value="7">
   7
  </option>
  <option value="8">
   8
  </option>
  <option value="9">
   9
  </option>
  <option value="10">
   10
  </option>
  <option value="11">
   11
  </option>
  <option value="12">
   12
  </option>
  <option value="13">
   13
  </option>
  <option value="14">
   14
  </option>
  <option value="15">
   15
  </option>
  <option value="16">
   16
  </option>
  <option value="17">
   17
  </option>
  <option value="18">
   18
  </option>
  <option value="19">
   19
  </option>
  <option value="20">
   20
  </option>
  <option value="21">
   21
  </option>
  <option value="22">
   22
  </option>
  <option value="23">
   23
  </option>
  <option value="24">
   24
  </option>
  <option value="25">
   25
  </option>
  <option value="26">
   26
  </option>
  <option value="27">
   27
  </option>
  <option value="28">
   28
  </option>
  <option value="29">
   29
  </option>
  <option value="30">
   30
  </option>
  <option value="31">
   31
  </option>
 </select>
 <input id="Dt--foobar__year" maxlength="4" name="Dt--foobar__year" size="4" type="text" value="2008" />
 <select id="Dt--foobar__hour" name="Dt--foobar__hour">
  <option value="HH">
   HH
  </option>
  <option value="0">
   0
  </option>
  <option value="1">
   1
  </option>
  <option value="2">
   2
  </option>
  <option value="3">
   3
  </option>
  <option value="4">
   4
  </option>
  <option value="5">
   5
  </option>
  <option value="6">
   6
  </option>
  <option value="7">
   7
  </option>
  <option value="8">
   8
  </option>
  <option value="9">
   9
  </option>
  <option value="10">
   10
  </option>
  <option value="11">
   11
  </option>
  <option value="12">
   12
  </option>
  <option value="13">
   13
  </option>
  <option selected="selected" value="14">
   14
  </option>
  <option value="15">
   15
  </option>
  <option value="16">
   16
  </option>
  <option value="17">
   17
  </option>
  <option value="18">
   18
  </option>
  <option value="19">
   19
  </option>
  <option value="20">
   20
  </option>
  <option value="21">
   21
  </option>
  <option value="22">
   22
  </option>
  <option value="23">
   23
  </option>
 </select>
 :
 <select id="Dt--foobar__minute" name="Dt--foobar__minute">
  <option value="MM">
   MM
  </option>
  <option value="0">
   0
  </option>
  <option value="1">
   1
  </option>
  <option value="2">
   2
  </option>
  <option value="3">
   3
  </option>
  <option value="4">
   4
  </option>
  <option value="5">
   5
  </option>
  <option value="6">
   6
  </option>
  <option value="7">
   7
  </option>
  <option value="8">
   8
  </option>
  <option value="9">
   9
  </option>
  <option value="10">
   10
  </option>
  <option value="11">
   11
  </option>
  <option value="12">
   12
  </option>
  <option value="13">
   13
  </option>
  <option value="14">
   14
  </option>
  <option value="15">
   15
  </option>
  <option selected="selected" value="16">
   16
  </option>
  <option value="17">
   17
  </option>
  <option value="18">
   18
  </option>
  <option value="19">
   19
  </option>
  <option value="20">
   20
  </option>
  <option value="21">
   21
  </option>
  <option value="22">
   22
  </option>
  <option value="23">
   23
  </option>
  <option value="24">
   24
  </option>
  <option value="25">
   25
  </option>
  <option value="26">
   26
  </option>
  <option value="27">
   27
  </option>
  <option value="28">
   28
  </option>
  <option value="29">
   29
  </option>
  <option value="30">
   30
  </option>
  <option value="31">
   31
  </option>
  <option value="32">
   32
  </option>
  <option value="33">
   33
  </option>
  <option value="34">
   34
  </option>
  <option value="35">
   35
  </option>
  <option value="36">
   36
  </option>
  <option value="37">
   37
  </option>
  <option value="38">
   38
  </option>
  <option value="39">
   39
  </option>
  <option value="40">
   40
  </option>
  <option value="41">
   41
  </option>
  <option value="42">
   42
  </option>
  <option value="43">
   43
  </option>
  <option value="44">
   44
  </option>
  <option value="45">
   45
  </option>
  <option value="46">
   46
  </option>
  <option value="47">
   47
  </option>
  <option value="48">
   48
  </option>
  <option value="49">
   49
  </option>
  <option value="50">
   50
  </option>
  <option value="51">
   51
  </option>
  <option value="52">
   52
  </option>
  <option value="53">
   53
  </option>
  <option value="54">
   54
  </option>
  <option value="55">
   55
  </option>
  <option value="56">
   56
  </option>
  <option value="57">
   57
  </option>
  <option value="58">
   58
  </option>
  <option value="59">
   59
  </option>
 </select>
 :
 <select id="Dt--foobar__second" name="Dt--foobar__second">
  <option value="SS">
   SS
  </option>
  <option value="0">
   0
  </option>
  <option value="1">
   1
  </option>
  <option value="2">
   2
  </option>
  <option value="3">
   3
  </option>
  <option value="4">
   4
  </option>
  <option value="5">
   5
  </option>
  <option value="6">
   6
  </option>
  <option value="7">
   7
  </option>
  <option value="8">
   8
  </option>
  <option value="9">
   9
  </option>
  <option value="10">
   10
  </option>
  <option value="11">
   11
  </option>
  <option value="12">
   12
  </option>
  <option value="13">
   13
  </option>
  <option value="14">
   14
  </option>
  <option value="15">
   15
  </option>
  <option value="16">
   16
  </option>
  <option value="17">
   17
  </option>
  <option selected="selected" value="18">
   18
  </option>
  <option value="19">
   19
  </option>
  <option value="20">
   20
  </option>
  <option value="21">
   21
  </option>
  <option value="22">
   22
  </option>
  <option value="23">
   23
  </option>
  <option value="24">
   24
  </option>
  <option value="25">
   25
  </option>
  <option value="26">
   26
  </option>
  <option value="27">
   27
  </option>
  <option value="28">
   28
  </option>
  <option value="29">
   29
  </option>
  <option value="30">
   30
  </option>
  <option value="31">
   31
  </option>
  <option value="32">
   32
  </option>
  <option value="33">
   33
  </option>
  <option value="34">
   34
  </option>
  <option value="35">
   35
  </option>
  <option value="36">
   36
  </option>
  <option value="37">
   37
  </option>
  <option value="38">
   38
  </option>
  <option value="39">
   39
  </option>
  <option value="40">
   40
  </option>
  <option value="41">
   41
  </option>
  <option value="42">
   42
  </option>
  <option value="43">
   43
  </option>
  <option value="44">
   44
  </option>
  <option value="45">
   45
  </option>
  <option value="46">
   46
  </option>
  <option value="47">
   47
  </option>
  <option value="48">
   48
  </option>
  <option value="49">
   49
  </option>
  <option value="50">
   50
  </option>
  <option value="51">
   51
  </option>
  <option value="52">
   52
  </option>
  <option value="53">
   53
  </option>
  <option value="54">
   54
  </option>
  <option value="55">
   55
  </option>
  <option value="56">
   56
  </option>
  <option value="57">
   57
  </option>
  <option value="58">
   58
  </option>
  <option value="59">
   59
  </option>
 </select>
</span>

>>> fs.rebind(dt, data={'Dt--foo__day': 'DD', 'Dt--foo__month': '2', 'Dt--foo__year': '', 'Dt--bar__hour': 'HH', 'Dt--bar__minute': '6', 'Dt--bar__second': '8'})
>>> print pretty_html(fs.foo.render())
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
  <option value="3">
   March
  </option>
  <option value="4">
   April
  </option>
  <option value="5">
   May
  </option>
  <option value="6">
   June
  </option>
  <option value="7">
   July
  </option>
  <option value="8">
   August
  </option>
  <option value="9">
   September
  </option>
  <option value="10">
   October
  </option>
  <option value="11">
   November
  </option>
  <option value="12">
   December
  </option>
 </select>
 <select id="Dt--foo__day" name="Dt--foo__day">
  <option selected="selected" value="DD">
   Day
  </option>
  <option value="1">
   1
  </option>
  <option value="2">
   2
  </option>
  <option value="3">
   3
  </option>
  <option value="4">
   4
  </option>
  <option value="5">
   5
  </option>
  <option value="6">
   6
  </option>
  <option value="7">
   7
  </option>
  <option value="8">
   8
  </option>
  <option value="9">
   9
  </option>
  <option value="10">
   10
  </option>
  <option value="11">
   11
  </option>
  <option value="12">
   12
  </option>
  <option value="13">
   13
  </option>
  <option value="14">
   14
  </option>
  <option value="15">
   15
  </option>
  <option value="16">
   16
  </option>
  <option value="17">
   17
  </option>
  <option value="18">
   18
  </option>
  <option value="19">
   19
  </option>
  <option value="20">
   20
  </option>
  <option value="21">
   21
  </option>
  <option value="22">
   22
  </option>
  <option value="23">
   23
  </option>
  <option value="24">
   24
  </option>
  <option value="25">
   25
  </option>
  <option value="26">
   26
  </option>
  <option value="27">
   27
  </option>
  <option value="28">
   28
  </option>
  <option value="29">
   29
  </option>
  <option value="30">
   30
  </option>
  <option value="31">
   31
  </option>
 </select>
 <input id="Dt--foo__year" maxlength="4" name="Dt--foo__year" size="4" type="text" value="" />
</span>
>>> print pretty_html(fs.bar.render())
<span id="Dt--bar">
 <select id="Dt--bar__hour" name="Dt--bar__hour">
  <option selected="selected" value="HH">
   HH
  </option>
  <option value="0">
   0
  </option>
  <option value="1">
   1
  </option>
  <option value="2">
   2
  </option>
  <option value="3">
   3
  </option>
  <option value="4">
   4
  </option>
  <option value="5">
   5
  </option>
  <option value="6">
   6
  </option>
  <option value="7">
   7
  </option>
  <option value="8">
   8
  </option>
  <option value="9">
   9
  </option>
  <option value="10">
   10
  </option>
  <option value="11">
   11
  </option>
  <option value="12">
   12
  </option>
  <option value="13">
   13
  </option>
  <option value="14">
   14
  </option>
  <option value="15">
   15
  </option>
  <option value="16">
   16
  </option>
  <option value="17">
   17
  </option>
  <option value="18">
   18
  </option>
  <option value="19">
   19
  </option>
  <option value="20">
   20
  </option>
  <option value="21">
   21
  </option>
  <option value="22">
   22
  </option>
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
  <option value="1">
   1
  </option>
  <option value="2">
   2
  </option>
  <option value="3">
   3
  </option>
  <option value="4">
   4
  </option>
  <option value="5">
   5
  </option>
  <option selected="selected" value="6">
   6
  </option>
  <option value="7">
   7
  </option>
  <option value="8">
   8
  </option>
  <option value="9">
   9
  </option>
  <option value="10">
   10
  </option>
  <option value="11">
   11
  </option>
  <option value="12">
   12
  </option>
  <option value="13">
   13
  </option>
  <option value="14">
   14
  </option>
  <option value="15">
   15
  </option>
  <option value="16">
   16
  </option>
  <option value="17">
   17
  </option>
  <option value="18">
   18
  </option>
  <option value="19">
   19
  </option>
  <option value="20">
   20
  </option>
  <option value="21">
   21
  </option>
  <option value="22">
   22
  </option>
  <option value="23">
   23
  </option>
  <option value="24">
   24
  </option>
  <option value="25">
   25
  </option>
  <option value="26">
   26
  </option>
  <option value="27">
   27
  </option>
  <option value="28">
   28
  </option>
  <option value="29">
   29
  </option>
  <option value="30">
   30
  </option>
  <option value="31">
   31
  </option>
  <option value="32">
   32
  </option>
  <option value="33">
   33
  </option>
  <option value="34">
   34
  </option>
  <option value="35">
   35
  </option>
  <option value="36">
   36
  </option>
  <option value="37">
   37
  </option>
  <option value="38">
   38
  </option>
  <option value="39">
   39
  </option>
  <option value="40">
   40
  </option>
  <option value="41">
   41
  </option>
  <option value="42">
   42
  </option>
  <option value="43">
   43
  </option>
  <option value="44">
   44
  </option>
  <option value="45">
   45
  </option>
  <option value="46">
   46
  </option>
  <option value="47">
   47
  </option>
  <option value="48">
   48
  </option>
  <option value="49">
   49
  </option>
  <option value="50">
   50
  </option>
  <option value="51">
   51
  </option>
  <option value="52">
   52
  </option>
  <option value="53">
   53
  </option>
  <option value="54">
   54
  </option>
  <option value="55">
   55
  </option>
  <option value="56">
   56
  </option>
  <option value="57">
   57
  </option>
  <option value="58">
   58
  </option>
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
  <option value="1">
   1
  </option>
  <option value="2">
   2
  </option>
  <option value="3">
   3
  </option>
  <option value="4">
   4
  </option>
  <option value="5">
   5
  </option>
  <option value="6">
   6
  </option>
  <option value="7">
   7
  </option>
  <option selected="selected" value="8">
   8
  </option>
  <option value="9">
   9
  </option>
  <option value="10">
   10
  </option>
  <option value="11">
   11
  </option>
  <option value="12">
   12
  </option>
  <option value="13">
   13
  </option>
  <option value="14">
   14
  </option>
  <option value="15">
   15
  </option>
  <option value="16">
   16
  </option>
  <option value="17">
   17
  </option>
  <option value="18">
   18
  </option>
  <option value="19">
   19
  </option>
  <option value="20">
   20
  </option>
  <option value="21">
   21
  </option>
  <option value="22">
   22
  </option>
  <option value="23">
   23
  </option>
  <option value="24">
   24
  </option>
  <option value="25">
   25
  </option>
  <option value="26">
   26
  </option>
  <option value="27">
   27
  </option>
  <option value="28">
   28
  </option>
  <option value="29">
   29
  </option>
  <option value="30">
   30
  </option>
  <option value="31">
   31
  </option>
  <option value="32">
   32
  </option>
  <option value="33">
   33
  </option>
  <option value="34">
   34
  </option>
  <option value="35">
   35
  </option>
  <option value="36">
   36
  </option>
  <option value="37">
   37
  </option>
  <option value="38">
   38
  </option>
  <option value="39">
   39
  </option>
  <option value="40">
   40
  </option>
  <option value="41">
   41
  </option>
  <option value="42">
   42
  </option>
  <option value="43">
   43
  </option>
  <option value="44">
   44
  </option>
  <option value="45">
   45
  </option>
  <option value="46">
   46
  </option>
  <option value="47">
   47
  </option>
  <option value="48">
   48
  </option>
  <option value="49">
   49
  </option>
  <option value="50">
   50
  </option>
  <option value="51">
   51
  </option>
  <option value="52">
   52
  </option>
  <option value="53">
   53
  </option>
  <option value="54">
   54
  </option>
  <option value="55">
   55
  </option>
  <option value="56">
   56
  </option>
  <option value="57">
   57
  </option>
  <option value="58">
   58
  </option>
  <option value="59">
   59
  </option>
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
{AttributeField(foo): [ValidationError('Invalid date',)]}

>>> fs.rebind(dt, data={'Dt--foo__day': 'DD', 'Dt--foo__month': 'MM', 'Dt--foo__year': 'YYYY', 'Dt--bar__hour': 'HH', 'Dt--bar__minute': '1', 'Dt--bar__second': 'SS', 'Dt--foobar__day': 'DD', 'Dt--foobar__month': 'MM', 'Dt--foobar__year': '', 'Dt--foobar__hour': 'HH', 'Dt--foobar__minute': 'MM', 'Dt--foobar__second': 'SS'})
>>> fs.validate()
False
>>> fs.errors
{AttributeField(bar): [ValidationError('Invalid time',)]}

>>> fs.rebind(dt, data={'Dt--foo__day': 'DD', 'Dt--foo__month': 'MM', 'Dt--foo__year': 'YYYY', 'Dt--bar__hour': 'HH', 'Dt--bar__minute': 'MM', 'Dt--bar__second': 'SS', 'Dt--foobar__day': '11', 'Dt--foobar__month': '2', 'Dt--foobar__year': '1951', 'Dt--foobar__hour': 'HH', 'Dt--foobar__minute': 'MM', 'Dt--foobar__second': 'SS'})
>>> fs.validate()
False
>>> fs.errors
{AttributeField(foobar): [ValidationError('Incomplete datetime',)]}
"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()
