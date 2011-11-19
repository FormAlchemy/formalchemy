# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy.types import TypeEngine, Integer, Float, String, Unicode, Text, Boolean, Date, DateTime, Time, Numeric, Interval

try:
    from sqlalchemy.types import LargeBinary
except ImportError:
    # SA < 0.6
    from sqlalchemy.types import Binary as LargeBinary

sa_types = set([Integer, Float, String, Unicode, Text, LargeBinary, Boolean, Date, DateTime, Time, Numeric, Interval])

class HTML5Email(String):
    """HTML5 email field"""

class HTML5Url(String):
    """HTML5 url field"""

class HTML5Number(Integer):
    """HTML5 number field"""

class HTML5Color(String):
    """HTML5 color field"""

class HTML5DateTime(DateTime):
    """HTML5 datetime field"""

class HTML5Date(Date):
    """HTML5 date field"""

class HTML5Time(Time):
    """HTML5 time field"""

class List(TypeEngine):
    def get_dbapi_type(self):
        raise NotImplementedError()

class Set(TypeEngine):
    def get_dbapi_type(self):
        raise NotImplementedError()

