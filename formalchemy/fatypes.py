# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy.types import TypeEngine, Integer, Float, String, Unicode, Text, Binary, Boolean, Date, DateTime, Time, Numeric, Interval

sa_types = set([Integer, Float, String, Unicode, Text, Binary, Boolean, Date, DateTime, Time, Numeric, Interval])

class List(TypeEngine):
    def get_dbapi_type(self):
        raise NotImplementedError()

class Set(TypeEngine):
    def get_dbapi_type(self):
        raise NotImplementedError()

