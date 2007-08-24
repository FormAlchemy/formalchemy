# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import webhelpers as h
from sqlalchemy.types import Boolean, DateTime, Date, Time

__all__ = ["formalchemy"]
__version__ = "0.1"

class formalchemy(object):
    """A class taking a SQLAlchemy mapped class as argument. This tool
       generates HTML forms from SQLAlchemy models."""

    INDENTATION = "  "

    def __init__(self, model):
        self.model = model

    def get_cols(self, **kwargs):
        """ Returns column names of `model`.

            The following keywords can be given:
            * `pk=True` - If set to False, it won't return primary key columns.
            * `fk=True` - If set to False, it won't return foreign key columns.
            * `exclude=[]` - This should be an iterable containing column names to exclude.
        """

        exclude = kwargs.get("exclude", [])
        pk = kwargs.get("pk", True)
        fk = kwargs.get("fk", True)
        pkcols = self.get_pks()
        fkcols = self.get_fks()

        columns = []

        for col in self.model.c.keys():
            if col in exclude:
                continue
            if col in pkcols and not pk:
                continue
            elif col in fkcols and not fk:
                continue
            columns.append(col)

        return columns

    def get_readonlys(self, **kwargs):
        """ Returns a list of columns that should be readonly.

            The following keywords can be given:
            * `readonly_pk=False` - This will prohibits changes to primary key columns if set to True.
            * `readonly_fk=False` - This will prohibits changes to foreign key columns if set to True.
            * `readonly=[]` - This should be an iterable containing column names to set as readonly.
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

    def get_unnulls(self):
        """ Returns a list of non-nullable columns. """
        return [col for col in self.model.c.keys() if not self.model.c[col].nullable]

    def get_bools(self):
        """ Returns a list of Boolean columns. """
        return [col for col in self.model.c.keys() if isinstance(self.model.c[col].type, Boolean)]

    def get_datetimes(self):
        """ Returns a list of DateTime columns. """
        return [col for col in self.model.c.keys() if isinstance(self.model.c[col].type, DateTime)]

    def get_dates(self):
        """ Returns a list of Date columns. """
        return [col for col in self.model.c.keys() if isinstance(self.model.c[col].type, Date)]

    def get_times(self):
        """ Returns a list of Time columns. """
        return [col for col in self.model.c.keys() if isinstance(self.model.c[col].type, Time)]

    def get_pks(self):
        """ Returns a list of primary key columns. """
        return [col for col in self.model.c.keys() if self.model.c[col].primary_key]

    def get_fks(self):
        """ Returns a list of foreign key columns. """
        return [col for col in self.model.c.keys() if self.model.c[col].foreign_key]

    def get_default(self, col):
        """ Returns column `col`'s default or None. """
        if self.model.c[col].default:
            return self.model.c[col].default.arg
        return None

    def get_value(self, col):
        """ Returns column `col`'s current value. """
        return 

    def make_fields(self, **options):
        """ Returns HTML fields generated from an SQLAlchemy model.

            The following keywords can be given:
            * `password=[]` - An iterable of column names that should be set as password fields.
            * `hidden=[]` - An iterable of column names that should be set as hidden fields.
            * `fileobj=[]` - An iterable of column names that should be set as file fields.
            * `dropdown={}` - A dict holding column names as keys, dicts as values. These dicts can contain 4 keys:
              1) `opts`: holds either:
                - an iterable of option names: `["small", "medium", "large"]`. Options will have the same name and value.
                - an iterable of option paired name/value: `[("small", "$0.99"), ("medium", "$1.29"), ("large", "$1.59")]`.
                - a dict where dict keys are option names and dict values are option values: `{"small":"$0.99", "medium":"$1.29", "large":"$1.59"}`.
              2) `selected=None`: a string or a container of strings (when multiple select) that will set the "selected" HTML tag to items that match the value.
              3) `multiple=None`: set the HTML tag "multiple" if it holds a non-zero value.
              4) `size=None`: an integer that will set the size of the menu. Browsers should change the menu from a dropdown to a listing.


{"meal":
    {"opts":[("Hamburger", "HB"),
             ("Cheeseburger", "CB"),
             ("Bacon Burger", "BB"),
             ("Roquefort Burger", "RB"),
             ("Pasta Burger", "RB"),
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
            * `errors={}` - Should be a dict holding the column name as the key and the error message as the value.
            * `docs={}` - Should be a dict holding the column name as the key and the help message as the value.
            * `cls_req="field_req"` - Sets the desired HTML class name for columns that are not nullable.
            * `cls_opt="field_opt"` - Same for nullable columns.
            * `cls_err=field_err` - Sets the class for error information text.
            * `cls_doc="field_doc"` - Sets the class for documentation text.

            It also takes the same keywords as `get_readonlys`.
        """

        # Categorize columns
        columns = self.get_cols(**options)
        readonlys = self.get_readonlys(**options)
        unnullables = self.get_unnulls()
        booleans = self.get_bools()
        datetimes = self.get_datetimes()
        dates = self.get_dates()
        times = self.get_times()
        passwords = options.get('password', [])
        hiddens = options.get('hidden', [])
        dropdowns = options.get('dropdown', {})
        radios = options.get('radio', {})
        fileobj = options.get('file', [])

        errors = options.get('errors', {})
        docs = options.get('docs', {})

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
                field = h.hidden_field(col, value=getattr(self.model, col))
                html.append(field)
                continue

            params = {}
            params['name'] = col
            params['display'] = params['name'].replace("_", " ").capitalize()
            params['labelfor'] = params['name']
            if col in unnullables:
                params['class'] = class_required
            else:
                params['class'] = class_optional

            # Make the label
            field = h.content_tag("label", content=params['display'], for_=params['labelfor'], class_=params['class'])

            # Make the input
            if col in fileobj:
                field += "\n" + h.file_field(col)

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
                value = getattr(self.model, col)
                if value is None:
                    field += "\n" + h.check_box(col, default, checked=default)
                else:
                    field += "\n" + h.check_box(col, value, checked=value)

            elif hasattr(self.model.c[col].type, "length"):
                if col in passwords:
                    field += "\n" + h.password_field(col, value=getattr(self.model, col), maxlength=self.model.c[col].type.length, readonly=col in readonlys)
                else:
                    field += "\n" + h.text_field(col, value=getattr(self.model, col), maxlength=self.model.c[col].type.length, readonly=col in readonlys)

            else:
                field += "\n" + h.text_field(col, value=getattr(self.model, col), readonly=col in readonlys)

            # Make the error
            if col in errors:
                field += "\n" + h.content_tag("span", content=errors[col], class_=class_error)
            # Make the documentation
            if col in docs:
                field += "\n" + h.content_tag("span", content=docs[col], class_=class_doc)

            # Wrap the whole thing into a div
            field = self.wrap("<div>", field, "</div>")

            html.append(field)

        return "\n".join(html)

    def wrap(self, start, txt, end):
        return "\n".join([start, self.indent(txt), end])

    def indent(self, txt):
        return "\n".join([self.INDENTATION + i for i in txt.splitlines()])
