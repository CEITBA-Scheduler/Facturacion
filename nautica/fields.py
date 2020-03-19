from django.core.validators import EMPTY_VALUES
from django.forms import ValidationError, fields
from django.utils.translation import ugettext_lazy as _


class DNIField(fields.CharField):
    """
    A field that validates 'Documento Nacional de Identidad' (DNI) numbers.
    """
    default_error_messages = {
        'invalid': _("This field requires only numbers."),
        'max_digits': _("This field requires 7 or 8 digits."),
    }

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 10
        kwargs['min_length'] = 7

        super(DNIField, self).__init__(*args, **kwargs)

    def clean(self, value):
        """
        Value can be a string either in the [X]X.XXX.XXX or [X]XXXXXXX formats.
        """
        value = super(DNIField, self).clean(value)
        if value in EMPTY_VALUES:
            return ''
        if not value.isdigit():
            value = value.replace('.', '')
        if not value.isdigit():
            raise ValidationError(self.error_messages['invalid'])
        if len(value) not in (7, 8):
            raise ValidationError(self.error_messages['max_digits'])

        return value
