# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import webhelpers as h
from sqlalchemy.types import Binary, Boolean, Date, DateTime, Integer, Numeric, String, Time

__all__ = ["formalchemy"]
__version__ = "0.1"

# FIXME 
# implement FieldMaker
# implement SelectField
# implement DropDownField
# Don't iterrate so much over the model to find out what the column types are.

INDENTATION = "  "

def wrap(start, text, end):
    return "\n".join([start, indent(text), end])

def indent(text):
    return "\n".join([INDENTATION + line for line in text.splitlines()])

class formalchemy(object):
    """The `Formalchemy` class.

    This is the class responsible for generating HTML form fields. It needs
    to be instantiate with a SQLAlchemy mapped class as argument. The
    SQLAlchemy mapped class is held under `model`.

    The one method to use is `make_fields`. This is the method that returns
    generated HTML code from the `model` object.

    FormAlchemy has some default behaviour set. It is configured to generate
    the most HTML possible that will reflect the `model` object. Although,
    you can configure FormAlchemy to behave differently, thus altering the
    generated HTML output by many ways:

      * By passing keyword options to the `make_fields` method:

        make_fields(pk=False, fk=False, exclude=["private_column"])

      These options are NOT persistant. You'll need to pass these options
      everytime you call `make_fields` or FormAlchemy will fallback to it's
      default behaviour. Passing keyword options is usually meant to alter
      the HTML output on the fly.

      * At the SQLAlchemy mapped class level, by creating a `FormAlchemy`
      subclass, it is possible to setup attributes which names and values
      correspond to the keyword options passed to `make_fields`:

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
    options are passed to `make_fields`.

    """

    def __init__(self, model):
        """Construct the `Formalchemy` class.

        Arguments are:

          `model`
            An SQLAlchemy mapped class. This is the reference class.

        """
        self.model = model

        # Configure class level options.
        if hasattr(self.model, "FormAlchemy"):
            self.options = dict([(k, v) for k, v in self.model.FormAlchemy.__dict__.items() if not k.startswith('_')])
        else:
            self.options = dict()

    def configure(self, **options):
        """Configure FormAlchemy's default behaviour.

        This will update FormAlchemy's default behaviour with the given
        keyword options. Any other previously set options will be kept intact.

        """
        self.options.update(options)

    def reconfigure(self, **options):
        """Reconfigure FormAlchemy's default behaviour from scratch.

        This will clear any previously set option and update FormAlchemy's
        default behaviour with the given keyword options.

        """

        self.options.clear()
        self.configure(**options)

    def get_cols(self, **kwargs):
        """Return column names of `self.model`.

        Keywords arguments:
        * `pk=True` - Won't return primary key columns if set to `False`.
        * `fk=True` - Won't return foreign key columns if set to `False`.
        * `exclude=[]` - An iterable containing column names to exclude.

        """

        exclude = kwargs.get("exclude", [])
        pk = kwargs.get("pk", True)
        fk = kwargs.get("fk", True)
        pkcols = self.get_pks()
        fkcols = self.get_fks()

        columns = []

        for col in self.model.c.keys():
#            print col, self.model.c[col].type, "#" * 100
            if col in exclude:
                continue
            if col in pkcols and not pk:
                continue
            elif col in fkcols and not fk:
                continue
            columns.append(col)

        return columns

    def get_readonlys(self, **kwargs):
        """Return a list of columns that should be readonly.

        Keywords arguments:
        * `readonly_pk=False` - Will prohibit changes to primary key columns if set to `True`.
        * `readonly_fk=False` - Will prohibit changes to foreign key columns if set to `True`.
        * `readonly=[]` - An iterable containing column names to set as readonly.

        """

        readonlys = kwargs.get("readonly", [])
        readonly_pk = kwargs.get("readonly_pk", False)
        readonly_fk = kwargs.get("readonly_fk", False)
        pkcols = self.get_pks()
        fkcols = self.get_fks()

        columns = []

        for col in self.model.c.keys():
            if col in pkcols and readonly_pk:
                columns.append(col)
            elif col in fkcols and readonly_fk:
                columns.append(col)
            elif col in readonlys:
                columns.append(col)

        return columns

    def get_binaries(self):
        """Return a list of Binary type columns."""
        return [col for col in self.model.c.keys() if isinstance(self.model.c[col].type, Binary)]

    def get_booleans(self):
        """Return a list of Boolean type columns."""
        return [col for col in self.model.c.keys() if isinstance(self.model.c[col].type, Boolean)]

    def get_dates(self):
        """Return a list of Date type columns."""
        return [col for col in self.model.c.keys() if isinstance(self.model.c[col].type, Date)]

    def get_datetimes(self):
        """Return a list of DateTime type columns."""
        return [col for col in self.model.c.keys() if isinstance(self.model.c[col].type, DateTime)]

    def get_integers(self):
        """Return a list of Integer type columns."""
        return [col for col in self.model.c.keys() if isinstance(self.model.c[col].type, Integer)]

    def get_numerics(self):
        """Return a list of Numeric type columns."""
        return [col for col in self.model.c.keys() if isinstance(self.model.c[col].type, Numeric)]

    def get_strings(self):
        """Return a list of String type columns."""
        return [col for col in self.model.c.keys() if isinstance(self.model.c[col].type, String)]

    def get_times(self):
        """Return a list of Time type columns."""
        return [col for col in self.model.c.keys() if isinstance(self.model.c[col].type, Time)]

    def get_unnullables(self):
        """Return a list of non-nullable columns."""
        return [col for col in self.model.c.keys() if not self.model.c[col].nullable]

    def get_pks(self):
        """Return a list of primary key columns."""
        return [col for col in self.model.c.keys() if self.model.c[col].primary_key]

    def get_fks(self):
        """Return a list of foreign key columns."""
        return [col for col in self.model.c.keys() if self.model.c[col].foreign_key]

    def get_default(self, col):
        """Return column `col`'s default value or None."""
        if self.model.c[col].default:
            return self.model.c[col].default.arg
        return None

    def make_fields(self, **options):
        """Return HTML fields generated from the SQLAlchemy `self.model`.

        Keywords arguments:
        * `password=[]` - An iterable of column names that should be set as password fields.
        * `hidden=[]` - An iterable of column names that should be set as hidden fields.
        * `dropdown={}` - A dict holding column names as keys, dicts as values. These dicts can contain 4 keys:
          1) `opts`: holds either:
            - an iterable of option names: `["small", "medium", "large"]`. Options will have the same name and value.
            - an iterable of paired option name/value: `[("small", "$0.99"), ("medium", "$1.29"), ("large", "$1.59")]`.
            - a dict where dict keys are option names and dict values are option values: `{"small":"$0.99", "medium":"$1.29", "large":"$1.59"}`.
          2) `selected=None`: a string or a container of strings (when multiple select) that will set the "selected" HTML tag to items that match the value.
          3) `multiple=None`: set the HTML tag "multiple" if it holds a non-zero value.
          4) `size=None`: an integer that will set the size of the menu. Browsers usually change the menu from a dropdown to a listing.

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

        # Merge class level options with argument level options.
        default_opts = self.options.copy()
        default_opts.update(**options)
        options = default_opts

        # Categorize columns
        columns = self.get_cols(**options)
        readonlys = self.get_readonlys(**options)
        unnullables = self.get_unnullables()

        # By type
        binaries = self.get_binaries()
        booleans = self.get_booleans()
        dates = self.get_dates()
        datetimes = self.get_datetimes()
        integers = self.get_integers()
        numerics = self.get_numerics()
        strings = self.get_strings()
        times = self.get_times()

        passwords = options.get('password', [])
        hiddens = options.get('hidden', [])
        dropdowns = options.get('dropdown', {})
        radios = options.get('radio', {})

        pretty_func = options.get('prettify')
        aliases = options.get('alias', {})

        errors = options.get('error', {})
        docs = options.get('doc', {})

        # Setup HTML class
#        class_label = options.get('cls_lab', 'form_label')
        class_required = options.get('cls_req', 'field_req')
        class_optional = options.get('cls_opt', 'field_opt')
        class_error = options.get('cls_err', 'field_err')
        class_doc = options.get('cls_doc', 'field_doc')

        html = []

        # Generate fields.
        for col in columns:

            # Get column's default value.
            default = self.get_default(col)

            # Process hidden fields first.
            if col in hiddens:
                html.append(str(HiddenField(self.model, col)))
                continue

            # Make the label
            label = Label(self.model, col)
            if callable(pretty_func):
                label.set_prettify(pretty_func)
            if col in unnullables:
                label.set_class(class_required)
            else:
                label.set_class(class_optional)
            field = str(label)

            # Make the input
            if col in binaries:
                field += "\n" + str(FileField(self.model, col))

            elif col in dropdowns:
                col_dict = dropdowns[col]
                opts = col_dict.get("opts")
                selected = col_dict.get("selected")
                multiple = col_dict.get("multiple")
                size = col_dict.get("size")
                field += "\n" + h.select(col, h.options_for_select(opts, selected=selected), multiple=multiple, size=size)

            elif col in radios:
                choices = radios[col]
                radiofields = []
                for choice in choices:
                    # Choice is a list/tuple...
                    if isinstance(choice, (list, tuple)):
                        if not len(choice) == 2:
                            raise ValueError, "Invalid radio button choice for '%s': %s. Paired sequence needed: (name, value)" % (col, repr(choice))
                        name, value = choice
                        checked = value == getattr(self.model, col) or value == default
                        radiofields.append("\n" + h.radio_button(col, value, checked=checked) + name)
                    # ... or just a string.
                    elif isinstance(choices, dict):
                        if not isinstance(choices[choice], basestring):
                            raise ValueError, "Invalid radio button choice for '%s': %s. Paired sequence needed: (name, value)" % (col, repr(choice))
                    else:
                        checked = choice == getattr(self.model, col) or choice == default
                        radiofields.append("\n" + h.radio_button(col, choice, checked=checked) + choice)
                field += "<br/>".join(radiofields)

            elif col in booleans:
                field += "\n" + str(BooleanField(self.model, col))

            elif col in strings:
                if col in passwords:
                    field += "\n" + str(PasswordField(self.model, col, readonly=col in readonlys))
                else:
                    field += "\n" + str(TextField(self.model, col))

            elif col in datetimes:
                field += "\n" + str(DateTimeField(self.model, col))

            elif col in dates:
                field += "\n" + str(DateField(self.model, col))

            elif col in times:
                field += "\n" + str(TimeField(self.model, col))

            elif col in integers:
                field += "\n" + str(IntegerField(self.model, col))

            else:
                field += "\n" + str(Field(self.model, col))

            # Make the error
            if col in errors:
                field += "\n" + h.content_tag("span", content=errors[col], class_=class_error)
            # Make the documentation
            if col in docs:
                field += "\n" + h.content_tag("span", content=docs[col], class_=class_doc)

            # Wrap the whole thing into a div
            field = wrap("<div>", field, "</div>")

            html.append(field)

        return "\n".join(html)


class FieldMaker(object):
    """The `FieldMaker` class.

    The `FieldMaker` class is responsible for generating the appropriate HTML
    code given a `Field` object.

    The generated HTML returned contains <label> and <input> tags.

    """

    html = ""

    def set_alias(self, alias):
        self.alias = alias

    def set_error(self, error):
        self.error = error

    def set_doc(self, doc):
        self.doc = doc

    def set_cls_req(self, cls_req):
        self.cls_req = cls_req

    def set_cls_opt(self, cls_opt):
        self.cls_opt = cls_opt

    def set_cls_err(self, cls_err):
        self.cls_err = cls_err

    def set_cls_doc(self, cls_doc):
        self.cls_doc = cls_doc

class Label(object):
    """The `Label` class."""

    name = None
    cls = None
    alias = None

    def __init__(self, model, col):
        self.name = col

    def set_class(self, cls):
        self.cls = cls

    def set_prettify(self, func):
        self.prettify = func

    def set_alias(self, alias):
        self.alias = alias

    def prettify(self, text):
        return text.replace("_", " ").capitalize()

    def get_display(self):
        if callable(self.prettify):
            return self.prettify(self.alias or self.name)
        return self.alias or self.name

    def __str__(self):
        return h.content_tag("label", content=self.get_display(), for_=self.name, class_=self.cls)

class Field(object):
    """The `Field` class. This is the base class for all fields objects."""

    name = None
    value = None
    default = None
    cls = None
    readonly = None

    def __init__(self, model, col, readonly=False):
        self.set_name(col)
        self.set_value(getattr(model, col))
        if model.c[col].default:
            self.set_default(model.c[col].default.arg)
        self.set_readonly(readonly)

    def set_name(self, name):
        self.name = name

    def set_value(self, value):
        self.value = value

    def set_default(self, default_value):
        self.default = default_value

    def set_class(self, cls):
        self.cls = cls

    def set_readonly(self, value):
        self.readonly = value

    def get_value(self):
        if self.value is not None:
            return self.value
        else:
            return self.default

#    def __str__(self):
#        return h.text_field(self.name, value=self.get_value(), readonly=self.readonly)

class TextField(Field):
    """The `TextField` class."""

    length = None

    def __init__(self, model, col, readonly=None):
        super(TextField, self).__init__(model, col, readonly=readonly)
        self.set_length(model.c[col].type.length)

    def set_length(self, length):
        self.length = length

    def __str__(self):
        return h.text_field(self.name, value=self.get_value(), maxlength=self.length, readonly=self.readonly)

class PasswordField(TextField):
    """The `PasswordField` class."""

    def __init__(self, model, col, readonly=None):
        super(PasswordField, self).__init__(model, col, readonly=readonly)

    def __str__(self):
        return h.password_field(self.name, value=self.get_value(), maxlength=self.length, readonly=self.readonly)

class HiddenField(Field):
    """The `HiddenField` class."""

    def __init__(self, model, col):
        super(HiddenField, self).__init__(model, col)

    def __str__(self):
        return h.hidden_field(self.name, value=self.get_value())

class BooleanField(Field):
    """The `BooleanField` class."""

    def __init__(self, model, col):
        super(BooleanField, self).__init__(model, col)

    def __str__(self):
        return h.check_box(self.name, self.get_value(), checked=self.get_value(), readonly=self.readonly)

class FileField(Field):
    """The `FileField` class."""

    def __init__(self, model, col):
        super(FileField, self).__init__(model, col)

    def __str__(self):
        return h.file_field(self.name, self.get_value(), readonly=self.readonly)

class IntegerField(Field):
    """The `IntegerField` class."""

    def __str__(self):
        return h.text_field(self.name, value=self.get_value(), readonly=self.readonly)

class DateTimeField(Field):
    """The `DateTimeField` class."""

    def __str__(self):
        return h.text_field(self.name, value=self.get_value(), readonly=self.readonly)


class DateField(Field):
    """The `DateField` class."""

    def __str__(self):
        return h.text_field(self.name, value=self.get_value(), readonly=self.readonly)


class TimeField(Field):
    """The `TimeField` class."""

    def __str__(self):
        return h.text_field(self.name, value=self.get_value(), readonly=self.readonly)

class SelectField(Field):
    """The `SelectField` class."""
    pass

class DropDownField(Field):
    """The `DropDownField` class."""
    pass
