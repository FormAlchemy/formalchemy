# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import webhelpers as h
from sqlalchemy.types import Binary, Boolean, Date, DateTime, Integer, Numeric, String, Time

__all__ = ["ModelRender", "FieldRender", "FieldSet", "TableItem", "TableCollection"]
__version__ = "0.2"
__doc__ = """
=Terminology=
  *model*: the SQLAlchemy mapped class.
"""

INDENTATION = "  "

def wrap(start, text, end):
    return "\n".join([start, indent(text), end])

def indent(text):
    return "\n".join([INDENTATION + line for line in text.splitlines()])

class FormAlchemyError(Exception):
    """Base FormAlchemy error class."""

class RenderError(FormAlchemyError):
    """Raised when an error occurs during rendering."""

class UnboundModelError(RenderError):
    """Raised when rendering is called but no model has been bound to it."""

    def __str__(self):
        return "No SQLAlchemy mapped class was bound to this class yet. Use the .bind() method."

class InvalidColumnError(RenderError):
    """Raised when column level rendering classes don't have a valid column set."""

class InvalidCollectionError(RenderError):
    """Raised when collection level rendering classes don't have a valid collection set."""

class FormAlchemyOptions(dict):
    """The `FormAlchemyOptions` dictionary class.

    This is the class responsible for parsing and holding FormAlchemy options.
    It has the same API as `dict`, plus three extra methods:

      * parse(self, model):
        Reconfigure options from scratch parsing the `model`'s FormAlchemy
        options.

      * configure(self, **options):
        Update options with the given option keywords.

      * reconfigure(self[, **options]):
        Reset the options and configure options given option keywords.

      * get_config(self):
        Return the current configuration.

    """

    def parse(self, model):
        """Parse options from `model`'s FormAlchemy subclass if defined."""
        self.clear()
        if hasattr(model, "FormAlchemy"):
            [self.__setitem__(k, v) for k, v in model.FormAlchemy.__dict__.items() if not k.startswith('_')]

    def configure(self, **options):
        """Configure FormAlchemy's default behaviour.

        This will update FormAlchemy's default behaviour with the given
        keyword options. Any other previously set options will be kept intact.

        """

        self.update(options)

    def reconfigure(self, **options):
        """Reconfigure `FormAlchemyOptions` from scratch.

        This will clear any previously set option and update FormAlchemy's
        default behaviour with the given keyword options. If no keyword option
        is passed, this will just reset all option.

        """

        self.clear()
        self.configure(**options)

    def get_config(self):
        return self

class BaseModel(object):
    """The `BaseModel` class.

    Takes a `model` as argument and provides convenient model methods.

    Methods:

      * bind(self, model)
      * is_bound(self)
      * is_pk(self, col):
      * get_pks(self):
      * get_fks(self):
      * is_nullable(self, col):
      * get_unnullables(self):
      * get_colnames(self[, **kwargs]):
      * get_readonlys(self[, **kwargs]):
      * get_coltypes(self):

    Inherits from FormAlchemyOptions methods as well.

    """

    def __init__(self, bind=None):
        self._options = FormAlchemyOptions()
        self.parse = self._options.parse
        self.configure = self._options.configure
        self.reconfigure = self._options.reconfigure
        self.get_config = self._options.get_config

        if bind:
            self.bind(bind)
        else:
            self._model = bind

    def bind(self, model):
        """Bind to the given `model` from which HTML field generation will be done."""

        self.parse(model)
        self._model = model

    def is_bound(self):
        """Return True if it was bound to a model. Otherwise, return False."""
        return bool(self._model)

    def is_pk(self, col):
        """Return True if `col` is a primary key column, otherwise return False."""
        return self._model.c[col].primary_key

    def get_pks(self):
        """Return a list of primary key column names."""
        return [col for col in self.get_colnames() if self.is_pk(col)]

    def is_fk(self, col):
        """Return True if `col` is a primary foreign column, otherwise return False."""
        return self._model.c[col].foreign_key

    def get_fks(self):
        """Return a list of foreign key column names."""
        return [col for col in self.get_colnames() if self.is_fk(col)]

    def is_nullable(self, col):
        """Return True if `col` is a nullable column, otherwise return False."""
        return self._model.c[col].nullable

    def get_unnullables(self):
        """Return a list of non-nullable column names."""
        return [col for col in self.get_colnames() if not self.is_nullable(col)]

    def get_colnames(self, **kwargs):
        """Return a list of filtered column names.

        Keyword arguments:
          * `pk=True` - Won't return primary key columns if set to `False`.
          * `fk=True` - Won't return foreign key columns if set to `False`.
          * `exclude=[]` - An iterable containing column names to exclude.

        """

        if not self.is_bound():
            raise UnboundModelError()

        if kwargs:
            return self._get_filtered_cols(**kwargs)
        return self._model.c.keys()

    def _get_filtered_cols(self, **kwargs):
        pk = kwargs.get("pk", True)
        fk = kwargs.get("fk", True)
        exclude = kwargs.get("exclude", [])

        ignore = exclude[:]
        if not pk:
            ignore.extend(self.get_pks())
        if not fk:
            ignore.extend(self.get_fks())

        columns = []

        for col in self.get_colnames():
            if not col in ignore:
                columns.append(col)

        return columns

    def get_readonlys(self, **kwargs):
        """Return a list of columns that should be readonly.

        Keywords arguments:
          * `readonly_pk=False` - Will prohibit changes to primary key columns if set to `True`.
          * `readonly_fk=False` - Will prohibit changes to foreign key columns if set to `True`.
          * `readonly=[]` - An iterable containing column names to set as readonly.

        """

        ro_pks = kwargs.get("readonly_pk", False)
        ro_fks = kwargs.get("readonly_fk", False)
        readonlys = kwargs.get("readonly", [])

        if ro_pks:
            readonlys += self.get_pks()
        if ro_fks:
            readonlys += self.get_fks()

        columns = []

        for col in self.get_colnames():
            if col in readonlys:
                columns.append(col)

        return columns

    def get_coltypes(self):
        """Categorize columns by type.

        Return a eight key dict. Each key is a direct subclass of TypeEngine:
          * `Binary=[]` - a list of Binary column names.
          * `Boolean=[]` - a list of Boolean column names.
          * `Date=[]` - a list of Date column names.
          * `DateTime=[]` - a list of DateTime column names.
          * `Integer=[]` - a list of Integer column names.
          * `Numeric=[]` - a list of Numeric column names.
          * `String=[]` - a list of String column names.
          * `Time=[]` - a list of Time column names.

        """

        # FIXME: What shall we do about non-standard SQLAlchemy types that were
        # built directly off of a TypeEngine type?
        # Although, this should handle custum types built from one of those 8.

        col_types = dict.fromkeys([t for t in [Binary, Boolean, Date, DateTime, Integer, Numeric, String, Time]], [])

        for t in col_types:
            col_types[t] = [col.name for col in self._model.c if isinstance(col.type, t)]

        return col_types

    def is_nullable(self, col):
        """Return True if `col` is a nullable column, otherwise return False."""
        return self._model.c[col].nullable

    def get_unnullables(self):
        """Return a list of non-nullable column names."""
        return [col for col in self._model.c.keys() if not self.is_nullable(col)]

    def get_pks(self):
        """Return a list of primary key column names."""
        return [col for col in self._model.c.keys() if self._model.c[col].primary_key]

    def get_fks(self):
        """Return a list of foreign key column names."""
        return [col for col in self._model.c.keys() if self._model.c[col].foreign_key]

    def set_prettify(self, func):
        if callable(func):
            self.prettify = func # Apply staticmethod(func) ?

    def prettify(text):
        """Return `text` prettify-ed.

        prettify("my_column_name") == "My column name"

        """
        return text.replace("_", " ").capitalize()

    prettify = staticmethod(prettify)

#    def __repr__(self):
#        repr = "%s bound to: %s" % (self.__class__.__name__, self._model)
#        return "<" + repr + ">"

class BaseRender(object):
    """The `BaseRender` class.

    This this is the base class for all classes needing rendering capabilities.
    The render method should be overridden with appropriate per class render
    method.

    """

    def render(self):
        if self.__class__.__name__ == "BaseRender":
            raise NotImplementedError()

        if not self.is_bound():
             raise UnboundModelError()

    def __str__(self):
        return self.render()

class BaseModelRender(BaseModel, BaseRender):
    """The `BaseModelRender` class.

    This this is the base class for all classes needing to deal with `model`
    access and support rendering capabilities. The render method should be
    overridden with appropriate render.

    """
    pass

class ModelRender(BaseModelRender):
    """Return generated HTML fields from a SQLAlchemy mapped class."""

    def render(self, **options):
        """Return HTML fields generated from the `model`.

        Keywords arguments:
        * `password=[]` - An iterable of column names that should be set as password fields.
        * `hidden=[]` - An iterable of column names that should be set as hidden fields.
        * `dropdown={}` - A dict holding column names as keys, dicts as values. These dicts have at least a `opts` key used for options. `opts` holds either:
            - an iterable of option names: `["small", "medium", "large"]`. Options will have the same name and value.
            - an iterable of paired option name/value: `[("small", "$0.99"), ("medium", "$1.29"), ("large", "$1.59")]`.
            - a dict where dict keys are option names and dict values are option values: `{"small":"$0.99", "medium":"$1.29", "large":"$1.59"}`.
            The `selected` key can also be set:
            `selected=value`: a string or a container of strings (when multiple values are selected) that will set the "selected" HTML tag to matching value options. It defaults to the SQLAlchemy mapped class's current value (if not None) or column default.
            Other keys can be given to be passed as standard HTML attributes, like multiple=<bool>, size=<integer> and so on.

{"meal":
    {"opts":[("Hamburger", "HB"),
             ("Cheeseburger", "CB"),
             ("Bacon Burger", "BB"),
             ("Roquefort Burger", "RB"),
             ("Pasta Burger", "PB"),
             ("Veggie Burger", "VB")],
     "selected":["CB", "BB"],    ## Or just "CB"
     "multiple":True,
     "size":3,
    }
}

        * `radio={}` - A dict holding column names as keys and an iterable as values. The iterable can hold:
          - input names: `["small", "medium", "large"]`. Inputs will have the same name and value.
          - paired name/value: `[("small", "$0.99"), ("medium", "$1.29"), ("large", "$1.59")]`.
          - a dict where dict keys are input names and dict values are input values: `{"small":"$0.99", "medium":"$1.29", "large":"$1.59"}`.

        * `prettify` - A function through which all label names will go. Defaults to: `"my_label".replace("_", " ").capitalize()`
        * `alias={}` - A dict holding the field name as the key and the alias name as the value. Note that aliases are beeing `prettify`ed as well.
        * `error={}` - A dict holding the field name as the key and the error message as the value.
        * `doc={}` - A dict holding the field name as the key and the help message as the value.
        * `cls_req="field_req"` - Sets the HTML class for fields that are not nullable (required).
        * `cls_opt="field_opt"` - Sets the HTML class for fields that are nullable (optional).
        * `cls_err=field_err` - Sets the HTML class for error messages.
        * `cls_doc="field_doc"` - Sets the HTML class for help messages.

        It also takes the same keywords as `get_readonlys`.

        """

        super(ModelRender, self).render()

        # Merge class level options with given argument options.
        opts = FormAlchemyOptions(self.get_config())
        opts.configure(**options)

        # Filter out unnecessary columns.
        columns = self.get_colnames(**opts)

        html = []
        # Generate fields.
        field_render = FieldRender(bind=self._model)
        field_render.reconfigure()
        for col in columns:
            field_render.set_column(col)
            field = field_render.render(**opts)
            html.append(field)

        return "\n".join(html)

class BaseCollectionRender(BaseModelRender):
    """The `BaseCollectionRender` class.

    This should be the superclass for all classes needing collection rendering.
    Takes an extra `collection=[]` keyword argument as the collection list.

    Methods:
      * set_collection(self, collection):
        Set the collection to render.

      * get_collection(self):
        Return current collection set.

    """

    def __init__(self, collection=[], bind=None):
        super(BaseCollectionRender, self).__init__(bind=bind)
        self._collection = collection

    def set_collection(self, collection):
        if not isinstance(collection, (list, tuple)):
            raise InvalidCollectionError()
        self._collection = collection

    def get_collection(self):
        return self._collection

class BaseColumnRender(BaseModelRender):
    """The `BaseColumnRender` class.

    This should be the superclass for all classes that want column level
    rendering. Takes an extra `column=None` keyword argument as the concerned
    column name.

    Methods:
      * set_column(self, col_name):
        Set the column to render.

      * get_column(self):
        Return current column set.

    """

    def __init__(self, column=None, bind=None):
        super(BaseColumnRender, self).__init__(bind=bind)
        if column:
            self.set_column(column)
        else:
            self._column = None

    def set_column(self, column):
        if not isinstance(column, basestring):
            raise ValueError("Column name should be a string, found %s of type %s instead." % (repr(column), type(column)))
        self._column = column

    def get_column(self):
        return self._column

    def render(self):
        super(BaseColumnRender, self).render()
        if not isinstance(self._column, basestring):
            raise InvalidColumnError("Invalid column '%s'. Please specify an existing column name using .set_column() before rendering." % (self._column))

class FieldRender(BaseColumnRender):
    """The `FieldRender` class.

    Return generated <label> + <input> tags for one single column.

    """

    def render(self, **options):
        super(FieldRender, self).render()

        # Merge class level options with given argument options.
        opts = FormAlchemyOptions(self.get_config())
        opts.configure(**options)

        # Categorize options
        readonlys = self.get_readonlys(**opts)

        passwords = opts.get('password', [])
        hiddens = opts.get('hidden', [])
        dropdowns = opts.get('dropdown', {})
        radios = opts.get('radio', {})

        pretty_func = opts.get('prettify')
        aliases = opts.get('alias', {})

        errors = opts.get('error', {})
        docs = opts.get('doc', {})

        # Setup HTML classes
#        class_label = opts.get('cls_lab', 'form_label')
        class_required = opts.get('cls_req', 'field_req')
        class_optional = opts.get('cls_opt', 'field_opt')
        class_error = opts.get('cls_err', 'field_err')
        class_doc = opts.get('cls_doc', 'field_doc')

        # Process hidden fields first as they don't need a `Label`.
        if self._column in hiddens:
            return HiddenField(self._model, col).render()

        # Make the label
        label = Label(self._column, alias=aliases.get(self._column, self._column))
        label.set_prettify(pretty_func)
        if self.is_nullable(self._column):
            label.cls = class_optional
        else:
            label.cls = class_required
        field = label.render()

        # Hold a list of column names by type.
        col_types = self.get_coltypes()

        # Make the input
        if self._column in radios:
            radio = RadioSet(self._model, self._column, choices=radios[self._column])
            field += "\n" + radio.render()

        elif self._column in dropdowns:
            dropdown = SelectField(self._model, self._column, dropdowns[self._column].pop("opts"), **dropdowns[self._column])
            field += "\n" + dropdown.render()

        elif self._column in passwords:
            field += "\n" + PasswordField(self._model, self._column, readonly=self._column in readonlys).render()

        elif self._column in col_types[String]:
            field += "\n" + TextField(self._model, self._column).render()

        elif self._column in col_types[Integer]:
            field += "\n" + IntegerField(self._model, self._column).render()

        elif self._column in col_types[Boolean]:
            field += "\n" + BooleanField(self._model, self._column).render()

        elif self._column in col_types[DateTime]:
            field += "\n" + DateTimeField(self._model, self._column).render()

        elif self._column in col_types[Date]:
            field += "\n" + DateField(self._model, self._column).render()

        elif self._column in col_types[Time]:
            field += "\n" + TimeField(self._model, self._column).render()

        elif self._column in col_types[Binary]:
            field += "\n" + FileField(self._model, self._column).render()

        else:
            field += "\n" + Field(self._model, self._column).render()

        # Make the error
        if self._column in errors:
            field += "\n" + h.content_tag("span", content=errors[self._column], class_=class_error)
        # Make the documentation
        if self._column in docs:
            field += "\n" + h.content_tag("span", content=docs[self._column], class_=class_doc)

        # Wrap the whole thing into a div
        field = wrap("<div>", field, "</div>")

        return field

class FieldSet(BaseModelRender):
    """The `FieldSet` class.

    This class is responsible for generating HTML fieldsets from a given
    `model`.

    The one method to use is `render`. This is the method that returns
    generated HTML code from the `model` object.

    FormAlchemy has some default behaviour set. It is configured to generate
    the most HTML possible that will reflect the `model` object. Although,
    you can configure FormAlchemy to behave differently, thus altering the
    generated HTML output by many ways:

      * By passing keyword options to the `render` method:

        render(pk=False, fk=False, exclude=["private_column"])

      These options are NOT persistant. You'll need to pass these options
      everytime you call `render` or FormAlchemy will fallback to it's
      default behaviour. Passing keyword options is usually meant to alter
      the HTML output on the fly.

      * At the SQLAlchemy mapped class level, by creating a `FormAlchemy`
      subclass, it is possible to setup attributes which names and values
      correspond to the keyword options passed to `render`:

        class MyClass(object):
            class FormAlchemy:
                pk = False
                fk = False
                exclude = ["private_column"]

      These attributes are persistant and will be used as FormAlchemy's
      default behaviour.

      * By passing the keyword options to FormAlchemy's `configure` method.
      These options are persistant. and will be used as FormAlchemy's default
      behaviour.

        configure(pk=False, fk=False, exclude=["private_column"])

    Note: In any case, options set at the SQLAlchemy mapped class level or
    via the `configure` method will be overridden if these same keyword
    options are passed to `render`.

    """

    def render(self, **options):
        super(FieldSet, self).render()

        # Merge class level options with given argument options.
        opts = FormAlchemyOptions(self.get_config())
        opts.configure(**options)

        model_render = ModelRender(self._model)
        # Reset options and only render based given options
        model_render.reconfigure()
        html = model_render.render(**opts)

        legend = opts.pop('legend', None)
        # Setup class's name as default.
        if legend is None:
            legend_txt = self._model.__class__.__name__
        # Don't render a legend field.
        elif legend is False:
            return wrap("<fieldset>", html, "</fieldset>")
        # Use the user given string as the legend.
        elif isinstance(legend, basestring):
            legend_txt = legend

        html = h.content_tag('legend', legend_txt) + "\n" + html
        return wrap("<fieldset>", html, "</fieldset>")

class Label(BaseRender):
    """The `Label` class."""

    cls = None

    def __init__(self, col, **kwargs):
        self.name = col
        self.alias = kwargs.pop('alias', self.name)
        self.cls = kwargs.pop('cls', None)
        self.set_prettify(kwargs.pop('prettify'))

    def set_alias(self, alias):
        self.alias = alias

    def get_display(self):
        return self.prettify(self.alias)

    def render(self):
        return h.content_tag("label", content=self.get_display(), for_=self.name, class_=self.cls)

class BaseField(BaseRender):
    """The `BaseField` class.

    This is the class that fits to all HTML <input> structure.

    """

    def __init__(self, name, value):
        self.name = name
        self.value = value

class Field(BaseField):
    """The `Field` class.

    This class takes a SQLAlchemy mapped class as first argument and the column
    name to process as second argument. It maps the column name as the field
    name and the column's value as the field's value.

    Methods:
      * `get_value(self)`:
        Return the column's current value if not None, otherwise
        return the default column value if available.
      * `render(self)`:
        Return generated HTML.

    All xField classes inherit of this `Field` class.

    """

    def __init__(self, model, col, **kwargs):
        super(Field, self).__init__(col, getattr(model, col))
        if model.c[col].default:
            self.default = model.c[col].default.arg
        else:
            self.default = model.c[col].default
        self.attribs = kwargs

    def get_value(self):
        if self.value is not None:
            return self.value
        else:
            return self.default

    def render(self):
        return h.text_field(self.name, value=self.get_value())

class TextField(Field):
    """The `TextField` class."""

    def __init__(self, model, col, **kwargs):
        super(TextField, self).__init__(model, col, **kwargs)
        self.length = model.c[col].type.length

    def render(self):
        return h.text_field(self.name, value=self.get_value(), maxlength=self.length, **self.attribs)

class PasswordField(TextField):
    """The `PasswordField` class."""

    def render(self):
        return h.password_field(self.name, value=self.get_value(), maxlength=self.length, **self.attribs)

class HiddenField(Field):
    """The `HiddenField` class."""

    def render(self):
        return h.hidden_field(self.name, value=self.get_value(), **self.attribs)

class BooleanField(Field):
    """The `BooleanField` class."""

    def render(self):
        return h.check_box(self.name, self.get_value(), checked=self.get_value(), **self.attribs)

class FileField(Field):
    """The `FileField` class."""

    def render(self):
        # Do we need a value here ?
        return h.file_field(self.name, **self.attribs)

class IntegerField(Field):
    """The `IntegerField` class."""

    def render(self):
        return h.text_field(self.name, value=self.get_value(), **self.attribs)

class DateTimeField(Field):
    """The `DateTimeField` class."""

    def render(self):
        return h.text_field(self.name, value=self.get_value(), **self.attribs)


class DateField(Field):
    """The `DateField` class."""

    def render(self):
        return h.text_field(self.name, value=self.get_value(), **self.attribs)


class TimeField(Field):
    """The `TimeField` class."""

    def render(self):
        return h.text_field(self.name, value=self.get_value(), **self.attribs)

class RadioField(BaseField):
    """The `RadioField` class."""

    def __init__(self, name, value, **kwargs):
        super(RadioField, self).__init__(name, value)
        self.attribs = kwargs

    def render(self):
        return h.radio_button(self.name, self.value, **self.attribs)

class RadioSet(Field):
    """The `RadioSet` class."""

    def __init__(self, model, col, choices, **kwargs):
        super(RadioSet, self).__init__(model, col, **kwargs)

        radios = []

        if isinstance(choices, dict):
            choices = choices.items()

        for choice in choices:
            # Choice is a list/tuple...
            if isinstance(choice, (list, tuple)):
                choice_name, choice_value = choice
                radio = RadioField(self.name, choice_value, checked=self.get_value() == choice_value)
                radios.append(radio.render() + choice_name)
            # ... or just a string.
            else:
                checked = choice == getattr(self._model, col) or choice == default
                radiofields.append("\n" + h.radio_button(col, choice, checked=checked) + choice)

        self.radios = radios

    def render(self):
        return h.tag("br").join(self.radios)

class SelectField(Field):
    """The `SelectField` class."""

    def __init__(self, model, col, options, **kwargs):
        self.options = options
        selected = kwargs.pop('selected', None)
        super(SelectField, self).__init__(model, col, **kwargs)
        self.selected = selected or self.get_value()

    def render(self):
        return h.select(self.name, h.options_for_select(self.options, selected=self.selected), **self.attribs)

class TableHead(BaseColumnRender):
    """The `TableHead` class.

    This class is responsible for rendering a single table head cell '<th>'.

    """

    def render(self, **options):
        super(TableHead, self).render()

        # Merge class level options with given argument options.
        opts = FormAlchemyOptions(self.get_config())
        opts.configure(**options)

        self.set_prettify(opts.get('prettify'))
        alias = opts.get('alias', {}).get(self._column, self._column)

        return wrap("<th>", self.prettify(alias), "</th>")

class TableTHead(BaseModelRender):
    """The `TableTHead` class.

    This class is responsible for rendering a table's header row.

    """

    def render(self, **options):
        super(TableTHead, self).render()

        row = []
        for col in self.get_colnames(**options):
            th = TableHead(column=col, bind=self._model)
            row.append(th.render(**options))
        row = wrap("<tr>", "\n".join(row), "</tr>")

        return wrap("<thead>", row, "</thead>")

class TableData(BaseColumnRender):
    """The `TableData` class.

    This class is responsible for rendering a single table data cell '<td>'.

    """

    def render(self, **options):
        super(TableData, self).render()

        value = getattr(self._model, self._column)
        if isinstance(value, bool):
            value = h.content_tag("em", value)
        elif value is None:
            value = h.content_tag("em", self.prettify("not available."))
        return wrap("<td>", str(value), "</td>")

class TableRow(BaseModelRender):
    """The `TableRow` class.

    This class is responsible for rendering a table's single row from a
    `model`.

    """

    def render(self, **options):
        super(TableRow, self).render()

        row = []
        for col in self.get_colnames(**options):
            td = TableData(bind=self._model, column=col)
            td.reconfigure()
            row.append(td.render(**options))
        return wrap("<tr>", "\n".join(row), "</tr>")

class TableBody(BaseCollectionRender):
    """The `TableBody` class.

    This class is responsible for rendering a table's body from a collection
    of items.

    """

    def render(self, **options):
        super(TableBody, self).render()

        if not self._collection:
            msg = self.prettify("no %s." % self._model.__class__.__name__)
            td = wrap('<td colspan="%s">' % len(self.get_colnames(**options)), msg, "</td>")
            return wrap("<tbody>", wrap("<tr>", td, "</tr>"), "</tbody>")

        tbody = []
        for item in self._collection:
            tr = TableRow(bind=item)
            tr.reconfigure()
            tbody.append(tr.render(**options))
        return wrap("<tbody>", "\n".join(tbody), "</tbody>")

class TableItem(BaseModelRender):
    """The `TableItem` class.

    This class is responsible for rendering a table from a single item.

    """

    def render(self, **options):
        super(TableItem, self).render()

        tbody = []
        for col in self.get_colnames(**options):
            row = []
            th = TableHead(bind=self._model, column=col)
            th.reconfigure()
            row.append(th.render(**options))

            td = TableData(bind=self._model, column=col)
            td.reconfigure()
            row.append(td.render(**options))

            tbody.append(wrap("<tr>", "\n".join(row), "</tr>"))

        return wrap("<table>", wrap("<tbody>", "\n".join(tbody), "</tbody>"), "</table>")

class TableCollection(BaseCollectionRender):
    """The `TableCollection` class.

    This class is responsible for rendering a table from a collection of items.

    """

    def render(self, **options):
        super(TableCollection, self).render()

        table = []

        th = TableTHead(bind=self._model)
        th.reconfigure()
        table.append(th.render(**options))

        tb = TableBody(bind=self._model, collection=self._collection)
        tb.reconfigure()
        table.append(tb.render(**options))

        return wrap("<table>", "\n".join(table), "</table>")
