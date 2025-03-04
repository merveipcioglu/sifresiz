from rest_framework import serializers
from django.core.exceptions import ValidationError
from users.validators import PasswordValidator

class PasswordField(serializers.CharField):
    def __init__(self, **kwargs):
        kwargs.setdefault('style', {'input_type': 'password'})
        kwargs.setdefault('write_only', True)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        validator = PasswordValidator()
        try:
            validator.validate(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e.message))
        return value 