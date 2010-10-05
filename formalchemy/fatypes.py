# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy.types import TypeEngine, Integer, Float, String, Unicode, Text, Boolean, Date, DateTime, Time, Numeric, Interval

try:
    from sqlalchemy.types import LargeBinary
except ImportError:
    # SA < 0.6
    from sqlalchemy.types import Binary as LargeBinary

sa_types = set([Integer, Float, String, Unicode, Text, LargeBinary, Boolean, Date, DateTime, Time, Numeric, Interval])

class List(TypeEngine):
    def get_dbapi_type(self):
        raise NotImplementedError()

class Set(TypeEngine):
    def get_dbapi_type(self):
        raise NotImplementedError()

