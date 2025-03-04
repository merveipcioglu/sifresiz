from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import CustomUser, Interest
from .validators import PasswordValidator, UsernameValidator, ImageValidator

class SignupStep1Serializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number']

    def validate_phone_number(self, value):
        if CustomUser.get_by_phone(value):
            raise serializers.ValidationError('Phone number already exists')
        return value

class SignupStep3Serializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
     
       

        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password': 'Passwords do not match'
            })

        username_validator = UsernameValidator()
        try:
            username_validator.validate(data['username'])
        except ValidationError as e:
            raise serializers.ValidationError({
                'username': str(e.message)
            })
        if CustomUser.get_by_username(data['username']):
            raise serializers.ValidationError({
                'username': 'Username already exists'
            })

        password_validator = PasswordValidator()
        try:
            password_validator.validate(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError({
                'password': str(e.message)
            })

        return data

class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name']

class UpdateUserInterestsSerializer(serializers.Serializer):
    interests = serializers.ListField(
        child=serializers.IntegerField(),
        max_length=3 
    )

    def validate_interests(self, value):
        if len(value) > 3:
            raise serializers.ValidationError('Maximum 3 interests allowed')
            
        existing_interests = Interest.objects.filter(id__in=value)
        if len(existing_interests) != len(value):
            raise serializers.ValidationError('One or more interests do not exist')
            
        return value

    def update(self, instance, validated_data):
        instance.interests.set(validated_data['interests'])
        return instance

class UpdatePicturesSerializer(serializers.Serializer):
    profile_picture = serializers.ImageField(
        required=False,
        error_messages={
            'invalid_image': 'Invalid profile picture. Allowed formats: JPG, JPEG, PNG'
        }
    )
    banner_picture = serializers.ImageField(
        required=False,
        error_messages={
            'invalid_image': 'Invalid banner picture. Allowed formats: JPG, JPEG, PNG'
        }
    )

    def validate(self, data):
        image_validator = ImageValidator()
        
        if 'profile_picture' in data:
            try:
                image_validator.validate(data['profile_picture'], 'profile picture')
            except ValidationError as e:
                raise serializers.ValidationError(str(e))

        if 'banner_picture' in data:
            try:
                image_validator.validate(data['banner_picture'], 'banner picture')
            except ValidationError as e:
                raise serializers.ValidationError(str(e))

        return data

class SuggestedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'profile_picture', 
                 'count_post', 'count_followers', 'count_following']

