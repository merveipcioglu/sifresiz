from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

from ..utils import AESCipher

from ..models import CustomUser
from ..serializers import SignupStep1Serializer, SignupStep3Serializer
from ..utils import generate_verification_code, send_verification_sms, generate_username_suggestions, create_encrypted_response
from ..swagger import (
    signup_docs, 
    verify_phone_docs, 
    resend_code_docs,
    check_username_docs,
    check_phone_docs
)
import json


@swagger_auto_schema(method='post', **signup_docs)
@api_view(['POST'])
def signup(request):
    try:
      
        cipher = AESCipher()

       
        encrypted_payload = request.data.get('data')
        print("Received encrypted payload:", encrypted_payload)

        if not encrypted_payload:
            return Response(create_encrypted_response('This field is required.'), status=status.HTTP_400_BAD_REQUEST)

     
        try:
            decrypted_payload = cipher.decrypt(encrypted_payload)
            print("Decrypted Payload:", decrypted_payload)
        except Exception as e:
            print(f"Decryption failed: {e}")
            return Response(create_encrypted_response('Invalid encrypted data'), status=status.HTTP_400_BAD_REQUEST)

        if not decrypted_payload:
            return Response(create_encrypted_response('Invalid encrypted data'), status=status.HTTP_400_BAD_REQUEST)

        try:
            data = json.loads(decrypted_payload)
            print("Decrypted data as dictionary:", data)
        except json.JSONDecodeError as e:
            print(f"JSON decoding failed: {e}")
            return Response(create_encrypted_response('Invalid JSON format'), status=status.HTTP_400_BAD_REQUEST)

        step = data.get('step')
        print("Processing step:", step)
        
        if step == 1:
            phone_number = data.get('phone_number')
            print("Phone number:", phone_number)
            
            existing_user = CustomUser.objects.filter(
                phone_number=phone_number,
                phone_verified=False,
            ).first()
            
            if existing_user:
                existing_user.delete()

            serializer = SignupStep1Serializer(data=data)
            if not serializer.is_valid():
                print("Validation Errors:", serializer.errors)
                first_error = next(iter(serializer.errors.values()))[0]
                return Response(create_encrypted_response(first_error), status=status.HTTP_400_BAD_REQUEST)

            verification_code = generate_verification_code()
            temp_username = f"t_{str(uuid.uuid4())[:6]}"
            
            try: 
                user = CustomUser.objects.create_user(
                    username=temp_username,
                    **serializer.validated_data,
                    verification_code=verification_code,
                    verification_code_created=timezone.now(),
                    phone_verified=False
                )
                print("User created:", user)
            except Exception as e:
                print(f"User creation failed: {e}")
                return Response(create_encrypted_response('User creation failed'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            username_suggestions = generate_username_suggestions(
                serializer.validated_data['first_name'],
                serializer.validated_data['last_name']
            )
            
            if send_verification_sms(phone_number, verification_code):
                response_data = {
                    'user_id': user.id,
                    'next_step': 2,
                    'username_suggestions': username_suggestions 
                }
                print("Verification code sent successfully")
                return Response(create_encrypted_response('Verification code sent', response_data), status=status.HTTP_201_CREATED)
            else:
                user.delete()
                print("Failed to send verification code")
                return Response(create_encrypted_response('Failed to send verification code'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        elif step == 3:
            serializer = SignupStep3Serializer(data=data)
            if not serializer.is_valid():
                print("Validation Errors:", serializer.errors)
                first_error = next(iter(serializer.errors.values()))[0]
                return Response(create_encrypted_response(first_error), status=status.HTTP_400_BAD_REQUEST)

            try:
                user = CustomUser.objects.get(id=serializer.validated_data['user_id'])
                print("User found:", user)
            except CustomUser.DoesNotExist:
                print("User not found")
                return Response(create_encrypted_response('User not found'), status=status.HTTP_404_NOT_FOUND)

            if not user.phone_verified:
                print("Phone number not verified")
                return Response(create_encrypted_response('Phone number not verified'), status=status.HTTP_400_BAD_REQUEST)

            user.username = serializer.validated_data['username']
            user.set_password(serializer.validated_data['password'])
            user.is_active = True
            user.save()

            refresh = RefreshToken.for_user(user)
            response_data = {
                'user_id': user.id,
                'username': user.username,
                'token': str(refresh.access_token)
            }
            print("Registration completed successfully")
            return Response(create_encrypted_response('Registration completed', response_data), status=status.HTTP_201_CREATED)

        # Ensure a response is returned for any other step or missing step
        print("Invalid step")
        return Response(create_encrypted_response('Invalid step'), status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(f"Unexpected error: {e}")
        return Response(create_encrypted_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(method='post', **verify_phone_docs)
@api_view(['POST'])
def verify_phone(request):
    try:
      
        cipher = AESCipher()

        encrypted_payload = request.data.get('data')
        print("Received encrypted payload:", encrypted_payload)

        if not encrypted_payload:
            return Response(create_encrypted_response('This field is required.'), status=status.HTTP_400_BAD_REQUEST)

        try:
            decrypted_payload = cipher.decrypt(encrypted_payload)
            print("Decrypted Payload:", decrypted_payload)
        except Exception as e:
            print(f"Decryption failed: {e}")
            return Response(create_encrypted_response('Invalid encrypted data'), status=status.HTTP_400_BAD_REQUEST)

        if not decrypted_payload:
            return Response(create_encrypted_response('Invalid encrypted data'), status=status.HTTP_400_BAD_REQUEST)

    
        try:
            data = json.loads(decrypted_payload)
            print("Decrypted data as dictionary:", data)
        except json.JSONDecodeError as e:
            print(f"JSON decoding failed: {e}")
            return Response(create_encrypted_response('Invalid JSON format'), status=status.HTTP_400_BAD_REQUEST)

        user_id = data.get('user_id')
        verification_code = data.get('verification_code')

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response(create_encrypted_response('User not found'), status=status.HTTP_404_NOT_FOUND)

        if user.phone_verified:
            return Response(create_encrypted_response('Phone already verified'), status=status.HTTP_400_BAD_REQUEST)

        if user.verification_attempts >= 3:
            return Response(create_encrypted_response('Too many attempts. Please request a new code.'), status=status.HTTP_400_BAD_REQUEST)

        if user.verification_code != verification_code:
            user.verification_attempts += 1
            user.save()
            return Response(create_encrypted_response('Invalid verification code'), status=status.HTTP_400_BAD_REQUEST)

        time_elapsed = timezone.now() - user.verification_code_created
        if time_elapsed.total_seconds() > 180:  # 3 minutes
            return Response(create_encrypted_response('Verification code expired'), status=status.HTTP_400_BAD_REQUEST)

        user.phone_verified = True
        user.save()

        response_data = {
            'message': 'Phone verified successfully',
            'user_id': user.id,
            'next_step': 3
        }
        return Response(create_encrypted_response('Phone verified successfully', response_data), status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Unexpected error: {e}")
        return Response(create_encrypted_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(method='post', **resend_code_docs)
@api_view(['POST'])
def resend_verification_code(request):
    try:
     
        cipher = AESCipher()


        encrypted_payload = request.data.get('data')
        print("Received encrypted payload:", encrypted_payload)

        if not encrypted_payload:
            return Response(create_encrypted_response('This field is required.'), status=status.HTTP_400_BAD_REQUEST)

     
        try:
            decrypted_payload = cipher.decrypt(encrypted_payload)
            print("Decrypted Payload:", decrypted_payload)
        except Exception as e:
            print(f"Decryption failed: {e}")
            return Response(create_encrypted_response('Invalid encrypted data'), status=status.HTTP_400_BAD_REQUEST)

        if not decrypted_payload:
            return Response(create_encrypted_response('Invalid encrypted data'), status=status.HTTP_400_BAD_REQUEST)

        try:
            data = json.loads(decrypted_payload)
            print("Decrypted data as dictionary:", data)
        except json.JSONDecodeError as e:
            print(f"JSON decoding failed: {e}")
            return Response(create_encrypted_response('Invalid JSON format'), status=status.HTTP_400_BAD_REQUEST)

        user_id = data.get('user_id')

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response(create_encrypted_response('User not found'), status=status.HTTP_404_NOT_FOUND)

        if user.phone_verified:
            return Response(create_encrypted_response('Phone already verified'), status=status.HTTP_400_BAD_REQUEST)

        new_code = generate_verification_code()
        if send_verification_sms(user.phone_number, new_code):
            user.verification_code = new_code
            user.verification_code_created = timezone.now()
            user.verification_attempts = 0
            user.save()

            response_data = {
                'message': 'New verification code sent successfully',
                'user_id': user.id
            }
            return Response(create_encrypted_response('New verification code sent successfully', response_data), status=status.HTTP_200_OK)
        else:
            return Response(create_encrypted_response('Failed to send new verification code'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        print(f"Unexpected error: {e}")
        return Response(create_encrypted_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(method='post', **check_username_docs)
@api_view(['POST'])
def check_username(request):
    try:
        
        cipher = AESCipher()

        encrypted_payload = request.data.get('data')
        print("Received encrypted payload:", encrypted_payload)

        if not encrypted_payload:
            return Response(create_encrypted_response('This field is required.'), status=status.HTTP_400_BAD_REQUEST)

        try:
            decrypted_payload = cipher.decrypt(encrypted_payload)
            print("Decrypted Payload:", decrypted_payload)
        except Exception as e:
            print(f"Decryption failed: {e}")
            return Response(create_encrypted_response('Invalid encrypted data'), status=status.HTTP_400_BAD_REQUEST)

        if not decrypted_payload:
            return Response(create_encrypted_response('Invalid encrypted data'), status=status.HTTP_400_BAD_REQUEST)


        try:
            data = json.loads(decrypted_payload)
            print("Decrypted data as dictionary:", data)
        except json.JSONDecodeError as e:
            print(f"JSON decoding failed: {e}")
            return Response(create_encrypted_response('Invalid JSON format'), status=status.HTTP_400_BAD_REQUEST)

        username = data.get('username')
        print("Username:", username)
        if not username:
            return Response(create_encrypted_response('Username is required'), status=status.HTTP_400_BAD_REQUEST)
            
        exists = CustomUser.get_by_username(username)  # with hash control
        if exists:
            return Response(create_encrypted_response('Username already exists'), status=status.HTTP_409_CONFLICT)
            
        return Response(create_encrypted_response('Username is available'), status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return Response(create_encrypted_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(method='post', **check_phone_docs)
@api_view(['POST'])
def check_phone(request):
    try:
        
        cipher = AESCipher()


        encrypted_payload = request.data.get('data')
        print("Received encrypted payload:", encrypted_payload)

        if not encrypted_payload:
            return Response(create_encrypted_response('This field is required.'), status=status.HTTP_400_BAD_REQUEST)

       
        try:
            decrypted_payload = cipher.decrypt(encrypted_payload)
            print("Decrypted Payload:", decrypted_payload)
        except Exception as e:
            print(f"Decryption failed: {e}")
            return Response(create_encrypted_response('Invalid encrypted data'), status=status.HTTP_400_BAD_REQUEST)

        if not decrypted_payload:
            return Response(create_encrypted_response('Invalid encrypted data'), status=status.HTTP_400_BAD_REQUEST)

        try:
            data = json.loads(decrypted_payload)
            print("Decrypted data as dictionary:", data)
        except json.JSONDecodeError as e:
            print(f"JSON decoding failed: {e}")
            return Response(create_encrypted_response('Invalid JSON format'), status=status.HTTP_400_BAD_REQUEST)

        phone_number = data.get('phone_number')
        if not phone_number:
            return Response(create_encrypted_response('Phone number is required'), status=status.HTTP_400_BAD_REQUEST)

        exists = CustomUser.get_by_phone(phone_number)
        if exists:
            return Response(create_encrypted_response('Phone number already exists'), status=status.HTTP_409_CONFLICT)
            
        return Response(create_encrypted_response('Phone number is available'), status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return Response(create_encrypted_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR) 