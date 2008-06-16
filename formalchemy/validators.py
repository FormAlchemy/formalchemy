class ValidationException(Exception):
    def message(self):
        return self.args[0]
    message = property(message)

def required(value):
    if value is None or value == '':
        msg = isinstance(value, list) and 'Please select a value' or 'Please enter a value'
        raise ValidationException(msg)

def integer(value):
    try:
        return int(value)
    except:
        raise ValidationException('Value is not an integer')
    
def float_(value):
    try:
        return float(value)
    except:
        raise ValidationException('Value is not a number')

def currency(value):
    if '%.2f' % float_(value) != value:
        raise ValidationException('Please specify full currency value, including cents (e.g., 12.34)')
