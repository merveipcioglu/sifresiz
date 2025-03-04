from django.core.exceptions import ValidationError
import re

class PasswordValidator:
    """
    Password validation rules:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one special character
    """
    
    def __init__(self):
        self.password_regex = {
            'length': r'.{8,}',
            'uppercase': r'[A-Z]',
            'lowercase': r'[a-z]',
            'special': r'[!@#$%^&*(),.?":{}|<>]'
        }
        
        self.error_message = 'Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one special character.'
    
    def validate(self, password):
        for pattern in self.password_regex.values():
            if not re.search(pattern, password):
                raise ValidationError(self.error_message)
        
    def get_help_text(self):
        return self.error_message 


class ImageValidator:
    
    def __init__(self):
        self.allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
        self.max_size = 5 * 1024 * 1024  # 5MB
        
    def validate(self, image, image_type='image'):
        if not image:
            raise ValidationError(f'{image_type.title()} is required')
            
        if image.content_type not in self.allowed_types:
            raise ValidationError(
                f'Invalid {image_type}. Allowed formats: JPG, JPEG, PNG',
            )
            
        if image.size > self.max_size:
            raise ValidationError(
                f'Invalid {image_type}. Maximum size: 5MB',
              
            )
        

class UsernameValidator:
    def __init__(self):
        self.min_length = 3
        self.max_length = 30
        self.error_message = 'Username must be between 3 and 30 characters'
    
    def validate(self, username):
        if not (self.min_length <= len(username) <= self.max_length):
            raise ValidationError(self.error_message) 