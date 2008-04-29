"""
Number Helpers

Provides methods for converting numbers into formatted strings. Functions are provided for
phone numbers, currencies, percentages, precision, positional notation, and file size.

"""
# Last synced with Rails copy at Revision 6045 on Feb 7th, 2007.
import re
import warnings

def number_to_phone(number, area_code=False, delimiter="-", extension="", country_code=""):
    """
    Formats a ``number`` into a US phone number string.

    ``area_code``
        When enabled, adds parentheses around the area code. Defaults to False
    ``delimiter``
        The delimiter to use, defaults to "-"
    ``extension``
        Specifies an extension to add to the end of the generated number
    ``country_code``
        Sets the country code for the phone number
    
    Examples::
    
        >>> number_to_phone(1235551234)
        '123-555-1234'
        >>> number_to_phone(1235551234, area_code=True)
        '(123) 555-1234'
        >>> number_to_phone(1235551234, delimiter=" ")
        '123 555 1234'
        >>> number_to_phone(1235551234, area_code=True, extension=555)
        '(123) 555-1234 x 555'
        >>> number_to_phone(1235551234, country_code=1)
        '1-123-555-1234'
    """
    number = str(number).strip()
    if area_code:
        number = re.sub(r'([0-9]{1,3})([0-9]{3})([0-9]{4})', r'(\1) \2%s\3' % delimiter,
                        number)
    else:
        number = re.sub(r'([0-9]{1,3})([0-9]{3})([0-9]{4})', r'\1%s\2%s\3' % \
                        (delimiter, delimiter), number)
    if extension and str(extension).strip():
        number += " x %s" % extension
    if country_code:
        number = '%s%s%s' % (country_code, delimiter, number)
    return number

def number_to_currency(number, unit="$", precision=2, separator=".", delimiter=","):
    """
    Formats a ``number`` into a currency string. 
    
    ``precision``
        Indicates the level of precision. Defaults to 2
    ``unit``
        Sets the currency type, defaults to "$"
    ``separator``
        Used to set what the unit separation should be. Defaults to "."
    ``delimiter``
        The delimiter character to use, defaults to ","
    
    Examples::
    
        >>> number_to_currency(1234567890.50)
        '$1,234,567,890.50'
        >>> number_to_currency(1234567890.506)
        '$1,234,567,890.51'
        >>> number_to_currency(1234567890.50, unit="&pound;", separator=",", delimiter="")
        '&pound;1234567890,50'
    """
    if precision < 1:
        separator = ""
    parts = number_with_precision(number, precision).split('.')
    num = unit + number_with_delimiter(parts[0], delimiter)
    if len(parts) > 1:
        num += separator + parts[1]
    return num

def number_to_percentage(number, precision=3, separator="."):
    """
    Formats a ``number`` as into a percentage string. 
    
    ``precision``
        The level of precision, defaults to 3
    ``separator``
        The unit separator to be used. Defaults to "."
    
    Examples::
    
        >>> number_to_percentage(100)
        '100.000%'
        >>> number_to_percentage(100, precision=0)
        '100%'
        >>> number_to_percentage(302.0574, precision=2)
        '302.06%'
    """
    number = number_with_precision(number, precision)
    parts = number.split('.')
    if len(parts) < 2:
        return parts[0] + "%"
    else:
        return parts[0] + separator + parts[1] + "%"

def number_to_human_size(size, precision=1):
    """
    Returns a formatted-for-humans file size.

    ``precision``
        The level of precision, defaults to 1
    
    Examples::
    
        >>> number_to_human_size(123)
        '123 Bytes'
        >>> number_to_human_size(1234)
        '1.2 KB'
        >>> number_to_human_size(12345)
        '12.1 KB'
        >>> number_to_human_size(1234567)
        '1.2 MB'
        >>> number_to_human_size(1234567890)
        '1.1 GB'
        >>> number_to_human_size(1234567890123)
        '1.1 TB'
        >>> number_to_human_size(1234567, 2)
        '1.18 MB'
    """
    if size == 1:
        return "1 Byte"
    elif size < 1024:
        return "%d Bytes" % size
    elif size < (1024**2):
        return ("%%.%if KB" % precision) % (size / 1024.00)
    elif size < (1024**3):
        return ("%%.%if MB" % precision) % (size / 1024.00**2)
    elif size < (1024**4):
        return ("%%.%if GB" % precision) % (size / 1024.00**3)
    elif size < (1024**5):
        return ("%%.%if TB" % precision) % (size / 1024.00**4)
    else:
        return ""

def human_size(*args, **kwargs):
    """Deprecated: Use number_to_human_size instead."""
    warnings.warn('The human_size function has been deprecated, please use '
                  'number_to_human_size instead.', DeprecationWarning, 2)
    return number_to_human_size(*args, **kwargs)

def number_with_delimiter(number, delimiter=",", separator="."):
    """
    Formats a ``number`` with grouped thousands using ``delimiter``.
    
    ``delimiter``
        The delimiter character to use, defaults to ","
    ``separator``
        Used to set what the unit separation should be. Defaults to "."

    Example::
    
        >>> number_with_delimiter(12345678)
        '12,345,678'
        >>> number_with_delimiter(12345678.05)
        '12,345,678.05'
        >>> number_with_delimiter(12345678, delimiter=".")
        '12.345.678'
    """
    parts = str(number).split('.')
    parts[0] = re.sub(r'(\d)(?=(\d\d\d)+(?!\d))', r'\1%s' % delimiter, str(parts[0]))
    return separator.join(parts)

def number_with_precision(number, precision=3):
    """
    Formats a ``number`` with a level of ``precision``.
    
    ``precision``
        The level of precision, defaults to 3

    Example::
    
        >>> number_with_precision(111.2345)
        '111.234'
        >>> number_with_precision(111.2345, 2)
        '111.23'
    """
    formstr = '%01.' + str(precision) + 'f'
    return formstr % number

__all__ = ['number_to_phone', 'number_to_currency', 'number_to_percentage',
           'number_with_delimiter', 'number_with_precision', 'number_to_human_size',
           'human_size']
