from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

from ..models import CustomUser
from ..serializers import SignupStep1Serializer, SignupStep3Serializer
from ..utils import generate_verification_code, send_verification_sms, generate_username_suggestions
from ..swagger import (
    signup_docs, 
    verify_phone_docs, 
    resend_code_docs,
    check_username_docs,
    check_phone_docs
)

@swagger_auto_schema(method='post', **signup_docs)
@api_view(['POST'])
def signup(request):
    try:
        step = request.data.get('step')
        
        if step == 1:
            phone_number = request.data.get('phone_number')
            
           
            existing_user = CustomUser.objects.filter(
                phone_number=phone_number,
                phone_verified=False,
            ).first()
            
            if existing_user:
              
                existing_user.delete()

            serializer = SignupStep1Serializer(data=request.data)
            if not serializer.is_valid():
                first_error = next(iter(serializer.errors.values()))[0]
                return Response({
                    'message': first_error
                }, status=status.HTTP_400_BAD_REQUEST)

            verification_code = generate_verification_code()
            user = CustomUser.objects.create_user(
                username=f"temp_{str(uuid.uuid4())[:8]}", 
                **serializer.validated_data,
                verification_code=verification_code,
                verification_code_created=timezone.now(),
                phone_verified=False 
            )

            username_suggestions = generate_username_suggestions(
                serializer.validated_data['first_name'],
                serializer.validated_data['last_name']
            )
            
            if send_verification_sms(serializer.validated_data['phone_number'], verification_code):
                return Response({
                    'message': 'Verification code sent',
                    'user_id': user.id,
                    'next_step': 2,
                    'username_suggestions': username_suggestions 
                }, status=status.HTTP_201_CREATED)
            else:
                user.delete()
                return Response({
                    'status': 'error',
                    'message': 'Failed to send verification code'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        elif step == 3:
            serializer = SignupStep3Serializer(data=request.data)
            if not serializer.is_valid():
                first_error = next(iter(serializer.errors.values()))[0]
                return Response({
                    'message': first_error
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = CustomUser.objects.get(id=serializer.validated_data['user_id'])
            except CustomUser.DoesNotExist:
                return Response({
                    'message': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)

            if not user.phone_verified:
                return Response({
                    'message': 'Phone number not verified'
                }, status=status.HTTP_400_BAD_REQUEST)

            user.username = serializer.validated_data['username']
            user.set_password(serializer.validated_data['password'])
            user.is_active = True
            user.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Registration completed',
                'data': {
                    'user_id': user.id,
                    'username': user.username,
                    'token': str(refresh.access_token)
                }
            }, status=status.HTTP_201_CREATED)

        else:
            return Response({
                'message': 'Invalid step'
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(method='post', **verify_phone_docs)
@api_view(['POST'])
def verify_phone(request):
    try:
        user_id = request.data.get('user_id')
        verification_code = request.data.get('verification_code')
        
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        if user.phone_verified:
            return Response({
                'message': 'Phone already verified'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if user.verification_attempts >= 3:
            return Response({
                'message': 'Too many attempts. Please request a new code.'
            }, status.HTTP_400_BAD_REQUEST)
            
        if user.verification_code != verification_code:
            user.verification_attempts += 1
            user.save()
            return Response({
                'message': 'Invalid verification code'
            }, status.HTTP_400_BAD_REQUEST)
            
        time_elapsed = timezone.now() - user.verification_code_created
        if time_elapsed.total_seconds() > 180:  # 3 minutes
            return Response({
                'message': 'Verification code expired'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        user.phone_verified = True
        user.save()
        
        return Response({
            'message': 'Phone verified successfully',
            'user_id': user.id,
            'next_step': 3
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(method='post', **resend_code_docs)
@api_view(['POST'])
def resend_verification_code(request):
    try:
        user_id = request.data.get('user_id')
        
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user.phone_verified:
            return Response({
                'message': 'Phone already verified'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        new_code = generate_verification_code()
        if send_verification_sms(user.phone_number, new_code):
            user.verification_code = new_code
            user.verification_code_created = timezone.now()
            user.verification_attempts = 0
            user.save()
            
            return Response({
                'message': 'New verification code sent successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Failed to send new verification code'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(method='post', **check_username_docs)
@api_view(['POST'])
def check_username(request):
    try:
        username = request.data.get('username')
        if not username:
            return Response({
                'message': 'Username is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        exists = CustomUser.objects.filter(username=username).exists()
        if exists:
            return Response({
                'message': 'Username already exists'
            }, status=status.HTTP_409_CONFLICT) 
            
        return Response({
            'message': 'Username is available'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'message': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(method='post', **check_phone_docs)
@api_view(['POST'])
def check_phone(request):
    try:
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({
                'message': 'Phone number is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        exists = CustomUser.objects.filter(phone_number=phone_number).exists()
        if exists:
            return Response({
                'message': 'Phone number already exists'
            }, status=status.HTTP_409_CONFLICT)  
            
        return Response({
            'message': 'Phone number is available'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'message': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 