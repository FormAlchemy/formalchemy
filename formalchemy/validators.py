# todo pass field and value (so exception can refer to field name, for instance)

if 'any' not in locals():
    # pre-2.5 support
    def any(seq):
        """
        >>> any(xrange(10))
        True
        >>> any([0, 0, 0])
        False
        """
        for o in seq:
            if o:
                return True
        return False

class ValidationError(Exception):
    def message(self):
        return self.args[0]
    message = property(message)

def required(value):
    if value is None or value == '':
        msg = isinstance(value, list) and 'Please select a value' or 'Please enter a value'
        raise ValidationError(msg)

def integer(value):
    try:
        return int(value)
    except:
        raise ValidationError('Value is not an integer')
    
def float_(value):
    try:
        return float(value)
    except:
        raise ValidationError('Value is not a number')

def currency(value):
    if '%.2f' % float_(value) != value:
        raise ValidationError('Please specify full currency value, including cents (e.g., 12.34)')

def email(value):
    reserved = r'()<>@,;:\"[]'

    try:
        recipient, domain = value.split('@', 1)
    except ValueError:
        raise ValidationError('Missing @ sign')

    if any([ord(ch) < 32 for ch in value]):
        raise ValidationError('Control characters present')
    if any([ord(ch) > 127 for ch in value]):
        raise ValidationError('Non-ASCII characters present')
    
    # validate recipient
    if not recipient:
        raise ValidationError('Recipient must be non-empty')
    if recipient.endswith('.'):
        raise ValidationError("Recipient must not end with '.'")

    # quoted regions, aka the reason any regexp-based validator is wrong
    i = 0
    while i < len(recipient):
        if recipient[i] == '"' and (i == 0 or recipient[i - 1] == '.' or recipient[i - 1] == '"'):
            # begin quoted region -- reserved characters are allowed here.
            # (this implementation allows a few addresses not strictly allowed by rfc 822 --
            # for instance, a quoted region that ends with '\' appears to be illegal.)
            i += 1
            while i < len(recipient):
                if recipient[i] == '"': 
                    break # end of quoted region
                i += 1
            else: 
                raise ValidationError("Unterminated quoted section in recipient")
            i += 1
            if i < len(recipient) and recipient[i] != '.': 
                raise ValidationError("Quoted section must be followed by '@' or '.'")
            continue
        if recipient[i] in reserved: 
            raise ValidationError("Reserved character present in recipient")
        i += 1

    # validate domain
    if not domain:
        raise ValidationError('Domain must be non-empty')
    if domain.endswith('.'):
        raise ValidationError("Domain must not end with '.'")
    if '..' in domain:
        raise ValidationError("Domain must not contain '..'")
    if any([ch in reserved for ch in domain]):
        raise ValidationError("Reserved character present in domain")


# parameterized validators return the validation function
def maxlength(length):
    if length <= 0:
        raise ValueError('Invalid maximum length')
    def f(value):
        if len(value) > length:
            raise ValidationError('Value must be no more than %d characters long' % length)
    return f

def minlength(length):
    if length <= 0:
        raise ValueError('Invalid minimum length')
    def f(value):
        if len(value) < length:
            raise ValidationError('Value must be at least %d characters long' % length)
    return f

def regex(exp, errormsg='Invalid input'):
    import re
    if type(exp) != type(re.compile('')):
        exp = re.compile(exp)
    def f(value):
        if not exp.match(value):
            raise ValidationError(errormsg)
    return f

# possible others:
# oneof raises if input is not one of [or a subset of for multivalues] the given list of possibilities
# url(check_exists=False)
# address parts
# cidr
# creditcard number/securitycode (/expires?)
# whole-form validators
#   fieldsmatch
#   requiredipresent/missing

