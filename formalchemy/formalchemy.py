# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import webhelpers as h

INDENTATION = "  "

def wrap(start, text, end):
    return "\n".join([start, indent(text), end])

def indent(text):
    return "\n".join([INDENTATION + line for line in text.splitlines()])
