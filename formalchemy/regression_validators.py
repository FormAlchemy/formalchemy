from validators import *

__doc__ = """
>>> integer('1')
1
>>> integer('1.2')
Traceback (most recent call last):
...
ValidationError: Value is not an integer

>>> float_('1')
1.0
>>> float_('1.2')
1.2
>>> float_('asdf')
Traceback (most recent call last):
...
ValidationError: Value is not a number

>>> currency('asdf')
Traceback (most recent call last):
...
ValidationError: Value is not a number
>>> currency('1')
Traceback (most recent call last):
...
ValidationError: Please specify full currency value, including cents (e.g., 12.34)
>>> currency('1.0')
Traceback (most recent call last):
...
ValidationError: Please specify full currency value, including cents (e.g., 12.34)
>>> currency('1.00')

>>> required('asdf')
>>> required('')
Traceback (most recent call last):
...
ValidationError: Please enter a value

>>> minlength(0)('a')
Traceback (most recent call last):
...
ValueError: Invalid minimum length
>>> minlength(2)('a')
Traceback (most recent call last):
...
ValidationError: Value must be at least 2 characters long
>>> minlength(2)('ab')

>>> maxlength(0)('a')
Traceback (most recent call last):
...
ValueError: Invalid maximum length
>>> maxlength(1)('a')
>>> maxlength(1)('ab')
Traceback (most recent call last):
...
ValidationError: Value must be no more than 1 characters long

>>> regex('[A-Z]+$')('ASDF')
>>> regex('[A-Z]+$')('abc')
Traceback (most recent call last):
...
ValidationError: Invalid input
>>> import re
>>> pattern = re.compile('[A-Z]+$', re.I)
>>> regex(pattern)('abc')

>>> email('a+formalchemy@gmail.com')
>>> email('a+."<>"@gmail.com')
>>> email('a+."<>"."[]"@gmail.com')
>>> email('a+."<>@gmail.com')
Traceback (most recent call last):
...
ValidationError: Unterminated quoted section in recipient
>>> email('a+."<>""[]"@gmail.com')
Traceback (most recent call last):
...
ValidationError: Quoted section must be followed by '@' or '.'
>>> email('<>@gmail.com')
Traceback (most recent call last):
...
ValidationError: Reserved character present in recipient
>>> email(chr(0) + '@gmail.com')
Traceback (most recent call last):
...
ValidationError: Control characters present
>>> email(chr(129) + '@gmail.com')
Traceback (most recent call last):
...
ValidationError: Non-ASCII characters present
>>> email('')
>>> email('asdf')
Traceback (most recent call last):
...
ValidationError: Missing @ sign
>>> email('@')
Traceback (most recent call last):
...
ValidationError: Recipient must be non-empty
>>> email('a@')
Traceback (most recent call last):
...
ValidationError: Domain must be non-empty
>>> email('a@gmail.com.')
Traceback (most recent call last):
...
ValidationError: Domain must not end with '.'
>>> email('a@gmail..com')
Traceback (most recent call last):
...
ValidationError: Domain must not contain '..'
>>> email('a@gmail>com')
Traceback (most recent call last):
...
ValidationError: Reserved character present in domain
"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()
