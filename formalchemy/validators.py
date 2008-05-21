class ValidationException(Exception):
    def message(self):
        return self.args[0]
    message = property(message)

def required(value):
    if value is None or value == '':
        msg = isinstance(value, list) and 'Please select a value' or 'Please enter a value'
        raise ValidationException(msg)
