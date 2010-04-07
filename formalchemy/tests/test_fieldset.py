__doc__ = r"""
>>> from formalchemy.tests import *

>>> FieldSet.default_renderers = original_renderers.copy()

# some low-level testing first

>>> fs = FieldSet(order1)
>>> fs._raw_fields()
[AttributeField(id), AttributeField(user_id), AttributeField(quantity), AttributeField(user)]
>>> fs.user.name
'user_id'

>>> fs = FieldSet(bill)
>>> fs._raw_fields()
[AttributeField(id), AttributeField(email), AttributeField(password), AttributeField(name), AttributeField(orders)]
>>> fs.orders.name
'orders'

binding should not change attribute order:
>>> fs = FieldSet(User)
>>> fs_bound = fs.bind(User)
>>> fs_bound._fields.values()
[AttributeField(id), AttributeField(email), AttributeField(password), AttributeField(name), AttributeField(orders)]

>>> fs = FieldSet(User2)
>>> fs._raw_fields()
[AttributeField(user_id), AttributeField(address_id), AttributeField(name), AttributeField(address)]

>>> fs.render() #doctest: +ELLIPSIS
Traceback (most recent call last):
...
Exception: No session found...

>>> fs = FieldSet(One)
>>> fs.configure(pk=True, focus=None)
>>> fs.id.is_required()
True
>>> print fs.render()
<div>
 <label class="field_req" for="One--id">
  Id
 </label>
 <input id="One--id" name="One--id" type="text" />
</div>

>>> fs = FieldSet(Two)
>>> fs
<FieldSet with ['id', 'foo']>
>>> fs.configure(pk=True)
>>> fs
<FieldSet (configured) with ['id', 'foo']>
>>> print fs.render()
<div>
 <label class="field_req" for="Two--id">
  Id
 </label>
 <input id="Two--id" name="Two--id" type="text" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("Two--id").focus();
//]]>
</script>
<div>
 <label class="field_opt" for="Two--foo">
  Foo
 </label>
 <input id="Two--foo" name="Two--foo" type="text" value="133" />
</div>

>>> fs = FieldSet(Two)
>>> print fs.render()
<div>
 <label class="field_opt" for="Two--foo">
  Foo
 </label>
 <input id="Two--foo" name="Two--foo" type="text" value="133" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("Two--foo").focus();
//]]>
</script>

>>> fs = FieldSet(Two)
>>> fs.configure(options=[fs.foo.label('A custom label')])
>>> print fs.render()
<div>
 <label class="field_opt" for="Two--foo">
  A custom label
 </label>
 <input id="Two--foo" name="Two--foo" type="text" value="133" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("Two--foo").focus();
//]]>
</script>
>>> fs.configure(options=[fs.foo.label('')])
>>> print fs.render()
<div>
 <label class="field_opt" for="Two--foo">
 </label>
 <input id="Two--foo" name="Two--foo" type="text" value="133" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("Two--foo").focus();
//]]>
</script>

>>> fs = FieldSet(Two)
>>> assert fs.render() == configure_and_render(fs, include=[fs.foo])
>>> assert fs.render() == configure_and_render(fs, exclude=[fs.id])

>>> fs = FieldSet(Two)
>>> fs.configure(include=[fs.foo.hidden()])
>>> print fs.render()
<input id="Two--foo" name="Two--foo" type="hidden" value="133" />

>>> fs = FieldSet(Two)
>>> fs.configure(include=[fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')])])
>>> print fs.render()
<div>
 <label class="field_opt" for="Two--foo">
  Foo
 </label>
 <select id="Two--foo" name="Two--foo">
  <option value="value1">
   option1
  </option>
  <option value="value2">
   option2
  </option>
 </select>
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("Two--foo").focus();
//]]>
</script>

>>> fs = FieldSet(Two)
>>> assert configure_and_render(fs, include=[fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')])]) == configure_and_render(fs, options=[fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')])]) 
>>> print pretty_html(fs.foo.with_html(onblur='test()').render())
<select id="Two--foo" name="Two--foo" onblur="test()">
 <option value="value1">
  option1
 </option>
 <option value="value2">
  option2
 </option>
</select>
>>> print fs.foo.reset().with_html(onblur='test').render()
<input id="Two--foo" name="Two--foo" onblur="test" type="text" value="133" />

# Test with_metadata()
>>> fs = FieldSet(Three)
>>> fs.configure(include=[fs.foo.with_metadata(instructions=u'Answer well')])
>>> print fs.render()
<div>
 <label class="field_opt" for="Three--foo">
  Foo
 </label>
 <input id="Three--foo" name="Three--foo" type="text" />
 <span class="instructions">
  Answer well
 </span>
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("Three--foo").focus();
//]]>
</script>

# test sync
>>> print session.query(One).count()
0
>>> fs_1 = FieldSet(One, data={})
>>> fs_1.sync()
>>> session.flush()
>>> print session.query(One).count()
1
>>> session.rollback()

>>> twof = TwoFloat(id=1, foo=32.2)
>>> fs_twof = FieldSet(twof)
>>> print '%.1f' % fs_twof.foo.value
32.2
>>> print pretty_html(fs_twof.foo.render())
<input id="TwoFloat-1-foo" name="TwoFloat-1-foo" type="text" value="32.2" />

>>> import datetime
>>> twoi = TwoInterval(id=1, foo=datetime.timedelta(2.2))
>>> fs_twoi = FieldSet(twoi)
>>> fs_twoi.foo.renderer
<IntervalFieldRenderer for AttributeField(foo)>
>>> fs_twoi.foo.value
datetime.timedelta(2, 17280)
>>> print pretty_html(fs_twoi.foo.render())
<input id="TwoInterval-1-foo" name="TwoInterval-1-foo" type="text" value="2.17280" />
>>> fs_twoi.rebind(data={"TwoInterval-1-foo": "3.1"})
>>> fs_twoi.sync()
>>> new_twoi = fs_twoi.model
>>> new_twoi.foo == datetime.timedelta(3.1)
True

# test render and sync fatypes.Numeric
# http://code.google.com/p/formalchemy/issues/detail?id=41
>>> twon = TwoNumeric(id=1, foo=Decimal('2.3'))
>>> fs_twon = FieldSet(twon)
>>> print pretty_html(fs_twon.foo.render())
<input id="TwoNumeric-1-foo" name="TwoNumeric-1-foo" type="text" value="2.3" />
>>> fs_twon.rebind(data={"TwoNumeric-1-foo": "6.7"})
>>> fs_twon.sync()
>>> new_twon = fs_twon.model
>>> new_twon.foo == Decimal("6.7")
True

# test sync when TwoNumeric-1-foo is empty
>>> fs_twon.rebind(data={"TwoNumeric-1-foo": ""})
>>> fs_twon.sync()
>>> new_twon = fs_twon.model
>>> str(new_twon.foo)
'None'

>>> fs_cb = FieldSet(CheckBox)
>>> fs_cb.field.value is None
True
>>> print pretty_html(fs_cb.field.dropdown().render())
<select id="CheckBox--field" name="CheckBox--field">
 <option value="True">
  Yes
 </option>
 <option value="False">
  No
 </option>
</select>

# test no checkbox/radio submitted
>>> fs_cb.rebind(data={})
>>> fs_cb.field.raw_value is None
True
>>> fs_cb.field.value
False
>>> fs_cb.field.renderer.value is None
True
>>> print fs_cb.field.render()
<input id="CheckBox--field" name="CheckBox--field" type="checkbox" value="True" />
>>> fs_cb.field.renderer #doctest: +ELLIPSIS
<CheckBoxFieldRenderer for AttributeField(field)>
>>> fs_cb.field.renderer._serialized_value() is None
True
>>> print pretty_html(fs_cb.field.radio().render())
<input id="CheckBox--field_0" name="CheckBox--field" type="radio" value="True" />
<label for="CheckBox--field_0">
 Yes
</label>
<br />
<input id="CheckBox--field_1" name="CheckBox--field" type="radio" value="False" />
<label for="CheckBox--field_1">
 No
</label>

>>> fs_cb.validate()
True
>>> fs_cb.errors
{}
>>> fs_cb.sync()
>>> cb = fs_cb.model
>>> cb.field
False
>>> fs_cb.rebind(data={'CheckBox--field': 'True'})
>>> fs_cb.validate()
True
>>> fs_cb.sync()
>>> cb.field
True
>>> fs_cb.configure(options=[fs_cb.field.dropdown()])
>>> fs_cb.rebind(data={'CheckBox--field': 'False'})
>>> fs_cb.sync()
>>> cb.field
False

>>> fs = FieldSet(Two)
>>> print pretty_html(fs.foo.dropdown(options=['one', 'two']).radio().render())
<input id="Two--foo_0" name="Two--foo" type="radio" value="one" />
<label for="Two--foo_0">
 one
</label>
<br />
<input id="Two--foo_1" name="Two--foo" type="radio" value="two" />
<label for="Two--foo_1">
 two
</label>

>>> assert fs.foo.radio(options=['one', 'two']).render() == fs.foo.dropdown(options=['one', 'two']).radio().render()
>>> print fs.foo.radio(options=['one', 'two']).dropdown().render()
<select id="Two--foo" name="Two--foo">
<option value="one">one</option>
<option value="two">two</option>
</select>

>>> assert fs.foo.dropdown(options=['one', 'two']).render() == fs.foo.radio(options=['one', 'two']).dropdown().render()
>>> print pretty_html(fs.foo.dropdown(options=['one', 'two'], multiple=True).checkbox().render())
<input id="Two--foo_0" name="Two--foo" type="checkbox" value="one" />
<label for="Two--foo_0">
 one
</label>
<br />
<input id="Two--foo_1" name="Two--foo" type="checkbox" value="two" />
<label for="Two--foo_1">
 two
</label>

>>> fs = FieldSet(User)
>>> print fs.render()
<div>
 <label class="field_req" for="User--email">
  Email
 </label>
 <input id="User--email" maxlength="40" name="User--email" type="text" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("User--email").focus();
//]]>
</script>
<div>
 <label class="field_req" for="User--password">
  Password
 </label>
 <input id="User--password" maxlength="20" name="User--password" type="text" />
</div>
<div>
 <label class="field_opt" for="User--name">
  Name
 </label>
 <input id="User--name" maxlength="30" name="User--name" type="text" />
</div>
<div>
 <label class="field_opt" for="User--orders">
  Orders
 </label>
 <select id="User--orders" multiple="multiple" name="User--orders" size="5">
  <option value="2">
   Quantity: 5
  </option>
  <option value="3">
   Quantity: 6
  </option>
  <option value="1">
   Quantity: 10
  </option>
 </select>
</div>
>>> FieldSet(User).render() == FieldSet(User, session).render()
True

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
>>> print pretty_html(fs.orders.checkbox().render())
<input id="User-1-orders_0" name="User-1-orders" type="checkbox" value="2" />
<label for="User-1-orders_0">
 Quantity: 5
</label>
<br />
<input id="User-1-orders_1" name="User-1-orders" type="checkbox" value="3" />
<label for="User-1-orders_1">
 Quantity: 6
</label>
<br />
<input checked="checked" id="User-1-orders_2" name="User-1-orders" type="checkbox" value="1" />
<label for="User-1-orders_2">
 Quantity: 10
</label>

>>> print fs.orders.checkbox(options=session.query(Order).filter_by(id=1)).render()
<input checked="checked" id="User-1-orders_0" name="User-1-orders" type="checkbox" value="1" /><label for="User-1-orders_0">Quantity: 10</label>

>>> fs = FieldSet(bill, data={})
>>> fs.configure(include=[fs.orders.checkbox()])
>>> fs.validate()
True

>>> fs = FieldSet(bill, data={'User-1-orders': ['2', '3']})
>>> print pretty_html(fs.orders.render())
<select id="User-1-orders" multiple="multiple" name="User-1-orders" size="5">
 <option selected="selected" value="2">
  Quantity: 5
 </option>
 <option selected="selected" value="3">
  Quantity: 6
 </option>
 <option value="1">
  Quantity: 10
 </option>
</select>

>>> fs.orders.model_value
[1]
>>> fs.orders.raw_value
[<Order for user 1: 10>]

>>> fs = FieldSet(Two)
>>> print fs.foo.render()
<input id="Two--foo" name="Two--foo" type="text" value="133" />

>>> fs = FieldSet(Two)
>>> print fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')]).render()
<select id="Two--foo" name="Two--foo">
<option value="value1">option1</option>
<option value="value2">option2</option>
</select>

>>> fs = FieldSet(Order, session)
>>> print fs.render()
<div>
 <label class="field_req" for="Order--quantity">
  Quantity
 </label>
 <input id="Order--quantity" name="Order--quantity" type="text" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("Order--quantity").focus();
//]]>
</script>
<div>
 <label class="field_req" for="Order--user_id">
  User
 </label>
 <select id="Order--user_id" name="Order--user_id">
  <option value="1">
   Bill
  </option>
  <option value="2">
   John
  </option>
 </select>
</div>

# this seems particularly prone to errors; break it out in its own test
>>> fs = FieldSet(order1)
>>> fs.user.value
1

# test re-binding
>>> fs = FieldSet(Order)
>>> fs.configure(pk=True, options=[fs.quantity.hidden()])
>>> fs.rebind(order1)
>>> fs.quantity.value
10
>>> fs.session == object_session(order1)
True
>>> print fs.render()
<div>
 <label class="field_req" for="Order-1-id">
  Id
 </label>
 <input id="Order-1-id" name="Order-1-id" type="text" value="1" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("Order-1-id").focus();
//]]>
</script>
<input id="Order-1-quantity" name="Order-1-quantity" type="hidden" value="10" />
<div>
 <label class="field_req" for="Order-1-user_id">
  User
 </label>
 <select id="Order-1-user_id" name="Order-1-user_id">
  <option selected="selected" value="1">
   Bill
  </option>
  <option value="2">
   John
  </option>
 </select>
</div>

>>> fs = FieldSet(One)
>>> fs.configure(pk=True)
>>> print fs.render()
<div>
 <label class="field_req" for="One--id">
  Id
 </label>
 <input id="One--id" name="One--id" type="text" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("One--id").focus();
//]]>
</script>
>>> fs.configure(include=[])
>>> print fs.render()
<BLANKLINE>
>>> fs.configure(pk=True, focus=None)
>>> print fs.render()
<div>
 <label class="field_req" for="One--id">
  Id
 </label>
 <input id="One--id" name="One--id" type="text" />
</div>

>>> fs = FieldSet(One)
>>> fs.rebind(Two) #doctest: +ELLIPSIS
Traceback (most recent call last):
...
ValueError: ...

>>> fs = FieldSet(Two)
>>> fs.configure()
>>> fs2 = fs.bind(Two)
>>> [fs2 == field.parent for field in fs2._render_fields.itervalues()]
[True]

>>> fs = FieldSet(OTOParent, session)
>>> print fs.render()
<div>
 <label class="field_req" for="OTOParent--oto_child_id">
  Child
 </label>
 <select id="OTOParent--oto_child_id" name="OTOParent--oto_child_id">
  <option value="1">
   baz
  </option>
 </select>
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("OTOParent--oto_child_id").focus();
//]]>
</script>

>>> fs.rebind(parent)
>>> fs.child.raw_value
<OTOChild baz>

# validation + sync
>>> fs_2 = FieldSet(Two, data={'Two--foo': ''})
>>> fs_2.foo.value # '' is deserialized to None, so default of 133 is used
'133'
>>> fs_2.validate()
True
>>> fs_2.configure(options=[fs_2.foo.required()], focus=None)
>>> fs_2.validate()
False
>>> fs_2.errors
{AttributeField(foo): ['Please enter a value']}
>>> print fs_2.render()
<div>
 <label class="field_req" for="Two--foo">
  Foo
 </label>
 <input id="Two--foo" name="Two--foo" type="text" value="133" />
 <span class="field_error">
  Please enter a value
 </span>
</div>
>>> fs_2.rebind(data={'Two--foo': 'asdf'})
>>> fs_2.data
{'Two--foo': 'asdf'}
>>> fs_2.validate()
False
>>> fs_2.errors
{AttributeField(foo): [ValidationError('Value is not an integer',)]}
>>> print fs_2.render()
<div>
 <label class="field_req" for="Two--foo">
  Foo
 </label>
 <input id="Two--foo" name="Two--foo" type="text" value="asdf" />
 <span class="field_error">
  Value is not an integer
 </span>
</div>
>>> fs_2.rebind(data={'Two--foo': '2'})
>>> fs_2.data
{'Two--foo': '2'}
>>> fs_2.validate()
True
>>> fs_2.errors
{}
>>> fs_2.sync()
>>> fs_2.model.foo
2
>>> session.flush()
>>> print fs_2.render() #doctest: +ELLIPSIS
Traceback (most recent call last):
...
PkError: Primary key of model has changed since binding, probably due to sync()ing a new instance (from None to 1)...
>>> session.rollback()

>>> fs_1 = FieldSet(One, data={'One--id': '1'})
>>> fs_1.configure(pk=True)
>>> fs_1.validate()
True
>>> fs_1.sync()
>>> fs_1.model.id
1
>>> fs_1.rebind(data={'One--id': 'asdf'})
>>> fs_1.id.renderer.name
u'One--id'
>>> fs_1.validate()
False
>>> fs_1.errors
{AttributeField(id): [ValidationError('Value is not an integer',)]}

# test updating _bound_pk copy
>>> one = One(id=1)
>>> fs_11 = FieldSet(one)
>>> fs_11.id.renderer.name
u'One-1-id'
>>> one.id = 2
>>> fs_11.rebind(one)
>>> fs_11.id.renderer.name
u'One-2-id'

>>> fs_u = FieldSet(User, data={})
>>> fs_u.configure(include=[fs_u.orders])
>>> fs_u.validate()
True
>>> fs_u.sync()
>>> fs_u.model.orders
[]
>>> fs_u.rebind(User, session, data={'User--orders': [str(order1.id), str(order2.id)]})
>>> fs_u.validate()
True
>>> fs_u.sync()
>>> fs_u.model.orders == [order1, order2]
True
>>> session.rollback()

>>> fs_3 = FieldSet(Three, data={'Three--foo': 'asdf', 'Three--bar': 'fdsa'})
>>> fs_3.foo.value
'asdf'
>>> print fs_3.foo.textarea().render()
<textarea id="Three--foo" name="Three--foo">asdf</textarea>
>>> print fs_3.foo.textarea("3x4").render()
<textarea cols="3" id="Three--foo" name="Three--foo" rows="4">asdf</textarea>
>>> print fs_3.foo.textarea((3,4)).render()
<textarea cols="3" id="Three--foo" name="Three--foo" rows="4">asdf</textarea>
>>> fs_3.bar.value
'fdsa'
>>> def custom_validator(fs):
...   if fs.foo.value != fs.bar.value:
...     fs.foo.errors.append('does not match bar')
...     raise ValidationError('foo and bar do not match')
>>> fs_3.configure(global_validator=custom_validator, focus=None)
>>> fs_3.validate()
False
>>> sorted(fs_3.errors.items())
[(None, ('foo and bar do not match',)), (AttributeField(foo), ['does not match bar'])]
>>> print fs_3.render()
<div class="fieldset_error">
 foo and bar do not match
</div>
<div>
 <label class="field_opt" for="Three--foo">
  Foo
 </label>
 <input id="Three--foo" name="Three--foo" type="text" value="asdf" />
 <span class="field_error">
  does not match bar
 </span>
</div>
<div>
 <label class="field_opt" for="Three--bar">
  Bar
 </label>
 <input id="Three--bar" name="Three--bar" type="text" value="fdsa" />
</div>

# custom renderer
>>> fs_3 = FieldSet(Three, data={'Three--foo': 'http://example.com/image.png'})
>>> fs_3.configure(include=[fs_3.foo.with_renderer(ImgRenderer)])
>>> print fs_3.foo.render()
<img src="http://example.com/image.png">

# natural PKs
>>> fs_npk = FieldSet(NaturalOrder, session)
>>> print fs_npk.render()
<div>
 <label class="field_req" for="NaturalOrder--quantity">
  Quantity
 </label>
 <input id="NaturalOrder--quantity" name="NaturalOrder--quantity" type="text" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("NaturalOrder--quantity").focus();
//]]>
</script>
<div>
 <label class="field_req" for="NaturalOrder--user_email">
  User
 </label>
 <select id="NaturalOrder--user_email" name="NaturalOrder--user_email">
  <option value="nbill@example.com">
   Natural Bill
  </option>
  <option value="njohn@example.com">
   Natural John
  </option>
 </select>
</div>
>>> fs_npk.rebind(norder2, session, data={'NaturalOrder-2-user_email': nbill.email, 'NaturalOrder-2-quantity': str(norder2.quantity)})
>>> fs_npk.user_email.renderer.name
u'NaturalOrder-2-user_email'
>>> fs_npk.sync()
>>> fs_npk.model.user_email == nbill.email
True
>>> session.rollback()

# allow attaching custom attributes to wrappers
>>> fs = FieldSet(User)
>>> fs.name.baz = 'asdf'
>>> fs2 = fs.bind(bill)
>>> fs2.name.baz
'asdf'

# equality can tell an field bound to an instance is the same as one bound to a type
>>> fs.name == fs2.name
True

# Field
>>> fs = FieldSet(One)
>>> fs.add(Field('foo'))
>>> print configure_and_render(fs, focus=None)
<div>
 <label class="field_opt" for="One--foo">
  Foo
 </label>
 <input id="One--foo" name="One--foo" type="text" />
</div>

>>> fs = FieldSet(One)
>>> fs.add(Field('foo', types.Integer, value=2))
>>> fs.foo.value
2
>>> print configure_and_render(fs, focus=None)
<div>
 <label class="field_opt" for="One--foo">
  Foo
 </label>
 <input id="One--foo" name="One--foo" type="text" value="2" />
</div>
>>> fs.rebind(One, data={'One--foo': '4'})
>>> fs.sync()
>>> fs.foo.value
4

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

>>> fs = FieldSet(One)
>>> fs.add(Field('foo', types.Integer, value=2).dropdown(options=[('1', 1), ('2', 2)]))
>>> print configure_and_render(fs, focus=None)
<div>
 <label class="field_opt" for="One--foo">
  Foo
 </label>
 <select id="One--foo" name="One--foo">
  <option value="1">
   1
  </option>
  <option selected="selected" value="2">
   2
  </option>
 </select>
</div>

# test Field __hash__, __eq__
>>> fs.foo == fs.foo.dropdown(options=[('1', 1), ('2', 2)])
True

>>> fs2 = FieldSet(One)
>>> fs2.add(Field('foo', types.Integer, value=2))
>>> fs2.configure(options=[fs2.foo.dropdown(options=[('1', 1), ('2', 2)])], focus=None)
>>> fs.render() == fs2.render()
True

>>> fs_1 = FieldSet(One)
>>> fs_1.add(Field('foo', types.Integer, value=[2, 3]).dropdown(options=[('1', 1), ('2', 2), ('3', 3)], multiple=True))
>>> print configure_and_render(fs_1, focus=None)
<div>
 <label class="field_opt" for="One--foo">
  Foo
 </label>
 <select id="One--foo" multiple="multiple" name="One--foo" size="5">
  <option value="1">
   1
  </option>
  <option selected="selected" value="2">
   2
  </option>
  <option selected="selected" value="3">
   3
  </option>
 </select>
</div>
>>> fs_1.rebind(One, data={'One--foo': ['1', '2']})
>>> fs_1.sync()
>>> fs_1.foo.value
[1, 2]

# test attribute names
>>> fs = FieldSet(One)
>>> fs.add(Field('foo'))
>>> fs.foo == fs['foo']
True
>>> fs.add(Field('add'))
>>> fs.add == fs['add']
False

# change default renderer 
>>> class BooleanSelectRenderer(SelectFieldRenderer):
...     def render(self, **kwargs):
...         kwargs['options'] = [('Yes', True), ('No', False)]
...         return SelectFieldRenderer.render(self, **kwargs)
>>> d = dict(FieldSet.default_renderers)
>>> d[types.Boolean] = BooleanSelectRenderer
>>> fs = FieldSet(CheckBox)
>>> fs.default_renderers = d
>>> print fs.field.render()
<select id="CheckBox--field" name="CheckBox--field">
<option value="True">Yes</option>
<option value="False">No</option>
</select>

# test setter rejection
>>> fs = FieldSet(One)
>>> fs.id = fs.id.required()
Traceback (most recent call last):
...
AttributeError: Do not set field attributes manually.  Use append() or configure() instead

# join
>>> fs = FieldSet(Order__User)
>>> fs._fields.values()
[AttributeField(orders_id), AttributeField(orders_user_id), AttributeField(orders_quantity), AttributeField(users_id), AttributeField(users_email), AttributeField(users_password), AttributeField(users_name)]
>>> fs.rebind(session.query(Order__User).filter_by(orders_id=1).one())
>>> print configure_and_render(fs, focus=None)
<div>
 <label class="field_req" for="Order__User-1_1-orders_quantity">
  Orders quantity
 </label>
 <input id="Order__User-1_1-orders_quantity" name="Order__User-1_1-orders_quantity" type="text" value="10" />
</div>
<div>
 <label class="field_req" for="Order__User-1_1-users_email">
  Users email
 </label>
 <input id="Order__User-1_1-users_email" maxlength="40" name="Order__User-1_1-users_email" type="text" value="bill@example.com" />
</div>
<div>
 <label class="field_req" for="Order__User-1_1-users_password">
  Users password
 </label>
 <input id="Order__User-1_1-users_password" maxlength="20" name="Order__User-1_1-users_password" type="text" value="1234" />
</div>
<div>
 <label class="field_opt" for="Order__User-1_1-users_name">
  Users name
 </label>
 <input id="Order__User-1_1-users_name" maxlength="30" name="Order__User-1_1-users_name" type="text" value="Bill" />
</div>
>>> fs.rebind(session.query(Order__User).filter_by(orders_id=1).one(), data={'Order__User-1_1-orders_quantity': '5', 'Order__User-1_1-users_email': bill.email, 'Order__User-1_1-users_password': '5678', 'Order__User-1_1-users_name': 'Bill'})
>>> fs.validate()
True
>>> fs.sync()
>>> session.flush()
>>> session.refresh(bill)
>>> bill.password == '5678'
True
>>> session.rollback()

>>> FieldSet.default_renderers[Point] = PointFieldRenderer
>>> fs = FieldSet(Vertex)
>>> print pretty_html(fs.start.render())
<input id="Vertex--start-x" name="Vertex--start-x" type="text" value="" />
<input id="Vertex--start-y" name="Vertex--start-y" type="text" value="" />
>>> fs.rebind(Vertex)
>>> v = fs.model
>>> v.start = Point(1,2)
>>> v.end = Point(3,4)
>>> print pretty_html(fs.start.render())
<input id="Vertex--start-x" name="Vertex--start-x" type="text" value="1" />
<input id="Vertex--start-y" name="Vertex--start-y" type="text" value="2" />
>>> fs.rebind(v) # this exercises a session bugfix
>>> fs.session == session
True
>>> fs.rebind(data={'Vertex--start-x': '10', 'Vertex--start-y': '20', 'Vertex--end-x': '30', 'Vertex--end-y': '40'})
>>> fs.validate()
True
>>> fs.sync()
>>> session.flush()
>>> v.id
1
>>> session.refresh(v)
>>> v.start.x
10
>>> v.end.y
40
>>> session.rollback()

# readonly tests
>>> t = FieldSet(john)
>>> john.name = None
>>> t.configure(readonly=True)
>>> t.readonly
True
>>> print t.render()
<tbody>
 <tr>
  <td class="field_readonly">
   Email:
  </td>
  <td>
   john@example.com
  </td>
 </tr>
 <tr>
  <td class="field_readonly">
   Password:
  </td>
  <td>
   5678
  </td>
 </tr>
 <tr>
  <td class="field_readonly">
   Name:
  </td>
  <td>
  </td>
 </tr>
 <tr>
  <td class="field_readonly">
   Orders:
  </td>
  <td>
   Quantity: 5, Quantity: 6
  </td>
 </tr>
</tbody>
>>> session.rollback()
>>> session.refresh(john)

>>> fs_or = FieldSet(order1)
>>> print fs_or.user.render_readonly()
<a href="mailto:bill@example.com">Bill</a>

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

>>> out = FieldSet(OrderUserTag)
>>> list(sorted(out._fields))
['id', 'order_id', 'order_user', 'tag', 'user_id']
>>> print out.order_user.name
order_user
>>> out.order_user.is_raw_foreign_key
False
>>> out.order_user.is_composite_foreign_key
True
>>> list(sorted(out.render_fields))
['order_user', 'tag']
>>> print pretty_html(out.order_user.render())
<select id="OrderUserTag--order_user" name="OrderUserTag--order_user">
 <option value="(1, 1)">
  OrderUser(1, 1)
 </option>
 <option value="(1, 2)">
  OrderUser(1, 2)
 </option>
</select>
>>> out.rebind(data={'OrderUserTag--order_user': '(1, 2)', 'OrderUserTag--tag': 'asdf'})
>>> out.validate()
True
>>> out.sync()
>>> print out.model.order_user
OrderUser(1, 2)

>>> fs = FieldSet(Function)
>>> fs.configure(pk=True)
>>> fs.foo.render().startswith('<span')
True

>>> fs_r = FieldSet(Recursive)
>>> fs_r.parent_id.is_raw_foreign_key
True
>>> fs_r.rebind(data={'Recursive--foo': 'asdf'})
>>> fs_r.validate()
True

>>> fs_oo = FieldSet(OptionalOrder)
>>> fs_oo.configure(options=[fs_oo.user.with_null_as(('No user', ''))])
>>> fs_oo.user._null_option
('No user', '')
>>> print pretty_html(fs_oo.user.render())
<select id="OptionalOrder--user_id" name="OptionalOrder--user_id">
 <option selected="selected" value="">
  No user
 </option>
 <option value="1">
  Bill
 </option>
 <option value="2">
  John
 </option>
</select>

>>> fs_oo = FieldSet(OptionalOrder)
>>> fs_oo.rebind(data={'OptionalOrder--user_id': fs_oo.user_id._null_option[1], 'OptionalOrder--quantity': ''})
>>> fs_oo.validate()
True
>>> fs_oo.user_id.value is None
True

>>> fs_bad = FieldSet(One)
>>> fs_bad.configure(include=[Field('invalid')])
Traceback (most recent call last):
...
ValueError: Unrecognized Field `AttributeField(invalid)` in `include` -- did you mean to call append() first?

>>> fs_s = FieldSet(Synonym)
>>> fs_s._fields
{'foo': AttributeField(foo), 'id': AttributeField(id)}

>>> fs_prefix = FieldSet(Two, prefix="myprefix")
>>> print(fs_prefix.render())
<div>
 <label class="field_opt" for="myprefix-Two--foo">
  Foo
 </label>
 <input id="myprefix-Two--foo" name="myprefix-Two--foo" type="text" value="133" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("myprefix-Two--foo").focus();
//]]>
</script>

>>> fs_prefix.rebind(data={"myprefix-Two--foo": "42"})
>>> fs_prefix.validate()
True
>>> fs_prefix.sync()
>>> fs_prefix.model.foo
42

>>> fs_two = FieldSet(Two)
>>> fs_two.configure(options=[fs_two.foo.label('1 < 2')])
>>> print fs_two.render()
<div>
 <label class="field_opt" for="Two--foo">
  1 &lt; 2
 </label>
 <input id="Two--foo" name="Two--foo" type="text" value="133" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("Two--foo").focus();
//]]>
</script>

>>> fs_prop = FieldSet(Property)
>>> fs_prop.foo.is_readonly()
True

>>> fs_conflict = FieldSet(ConflictNames)
>>> fs_conflict.rebind(conflict_names)
>>> print fs_conflict.render() #doctest: +ELLIPSIS
<div>
...

"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()
