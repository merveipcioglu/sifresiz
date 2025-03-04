from rest_framework import serializers
from django.core.exceptions import ValidationError
from users.validators import PasswordValidator
from django.db import models
from .encryption import AESCipher, generate_hash

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

class EncryptedCharField(models.CharField):
    def __init__(self, *args, hash_field=None, **kwargs):
        self.hash_field = hash_field
        self.cipher = AESCipher()
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.cipher.decrypt(value)

    def to_python(self, value):
        if value is None:
            return value
        # Eğer değer zaten şifrelenmiş formatta ise (iv:ct formatında)
        if isinstance(value, str) and ':' in value and len(value.split(':')) == 2:
            try:
                # Şifrelenmiş veriyi doğrula
                decrypted = self.cipher.decrypt(value)
                if decrypted is not None:
                    # Veri zaten şifrelenmiş, olduğu gibi döndür
                    return value
            except:
                pass
        # Değer şifrelenmiş formatta değilse, normal işleme devam et
        return super().to_python(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        # Eğer değer zaten şifrelenmiş formatta ise (iv:ct formatında)
        if isinstance(value, str) and ':' in value and len(value.split(':')) == 2:
            try:
                # Şifrelenmiş veriyi doğrula
                decrypted = self.cipher.decrypt(value)
                if decrypted is not None:
                    # Veri zaten şifrelenmiş, olduğu gibi döndür
                    return value
            except:
                pass
        # Değer şifrelenmiş formatta değilse, şifrele
        return self.cipher.encrypt(value)

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)
        if self.hash_field and value:
            # Hash değerini oluştur ve modele ata
            hash_value = generate_hash(self.cipher.decrypt(value) if ':' in value else value)
            setattr(model_instance, self.hash_field, hash_value)
        return value

class EncryptedTextField(models.TextField):
    def __init__(self, *args, **kwargs):
        self.cipher = AESCipher()
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.cipher.decrypt(value)

    def to_python(self, value):
        if value is None:
            return value
        # Eğer değer zaten şifrelenmiş formatta ise (iv:ct formatında)
        if isinstance(value, str) and ':' in value and len(value.split(':')) == 2:
            try:
                # Şifrelenmiş veriyi doğrula
                decrypted = self.cipher.decrypt(value)
                if decrypted is not None:
                    # Veri zaten şifrelenmiş, olduğu gibi döndür
                    return value
            except:
                pass
        # Değer şifrelenmiş formatta değilse, normal işleme devam et
        return super().to_python(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        # Eğer değer zaten şifrelenmiş formatta ise (iv:ct formatında)
        if isinstance(value, str) and ':' in value and len(value.split(':')) == 2:
            try:
                # Şifrelenmiş veriyi doğrula
                decrypted = self.cipher.decrypt(value)
                if decrypted is not None:
                    # Veri zaten şifrelenmiş, olduğu gibi döndür
                    return value
            except:
                pass
        # Değer şifrelenmiş formatta değilse, şifrele
        return self.cipher.encrypt(value)


