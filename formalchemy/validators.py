class ValidationException(Exception):
    def message(self):
        return self.args[0]
    message = property(message)

def required(st):
    if not st:
        raise ValidationException('Please enter a value')

