# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy.orm.attributes import InstrumentedAttribute

INDENTATION = "  "

def wrap(start, text, end):
    return "\n".join([start, indent(text), end])

def indent(text):
    return "\n".join([INDENTATION + line for line in text.splitlines()])

def validate_columns(iterable):
    try:
        L = list(iterable)
    except:
        raise ValueError()
    if L and not isinstance(L[0], InstrumentedAttribute):
        raise ValueError()
    
