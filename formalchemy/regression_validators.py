from validators import *

__doc__ = """
>>> integer('1')
1
>>> integer('1.2')
Traceback (most recent call last):
...
ValidationException: Value is not an integer

>>> float_('1')
1.0
>>> float_('1.2')
1.2
>>> float_('asdf')
Traceback (most recent call last):
...
ValidationException: Value is not a number

>>> currency('asdf')
Traceback (most recent call last):
...
ValidationException: Value is not a number
>>> currency('1')
Traceback (most recent call last):
...
ValidationException: Please specify full currency value, including cents (e.g., 12.34)
>>> currency('1.0')
Traceback (most recent call last):
...
ValidationException: Please specify full currency value, including cents (e.g., 12.34)
>>> currency('1.00')

>>> required('asdf')
>>> required('')
Traceback (most recent call last):
...
ValidationException: Please enter a value
"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()
