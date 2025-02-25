import re
from django.core.exceptions import ValidationError


def validate_phone_number(value):
    pattern = r'^\+?1?\d{9,15}$'
    if not re.match(pattern, value):
        raise ValidationError('Номер телефона должен быть в формате +123456789. До 15 цифр.')
