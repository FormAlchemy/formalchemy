# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy.types import Integer, Float, String, Binary, Boolean, Date, DateTime, Time

sa_types = set([Integer, Float, String, Binary, Boolean, Date, DateTime, Time])

from datetime import date as _date, datetime as _datetime, time as _time
native_types = {
    int: Integer,
    float: Float,
    str: Binary,
    unicode: String,
    bool: Boolean,
    _date: Date,
    _datetime: DateTime,
    _time: Time
}
