import os
import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view, 
    authentication_classes, 
    permission_classes,
    parser_classes
)
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema

from ..models import Interest, CustomUser
from ..serializers import (
    UpdateUserInterestsSerializer,
    UpdatePicturesSerializer,
    SuggestedUserSerializer,
    InterestSerializer
)
from ..utils import upload_file_to_s3, delete_file_from_s3, create_encrypted_response
from ..swagger import (
    update_interests_docs, 
    update_pictures_docs, 
    list_interests_docs,
    get_suggestions_docs
)
from ..utils import AESCipher

@swagger_auto_schema(method='post', **update_pictures_docs)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_pictures(request):
    try:
        # Initialize the cipher
        cipher = AESCipher()

        # Get the encrypted payload from the request
        encrypted_payload = request.data.get('data')
        print("Received encrypted payload:", encrypted_payload)

        if not encrypted_payload:
            return Response(create_encrypted_response('This field is required.'), status=status.HTTP_400_BAD_REQUEST)

        # Decrypt the payload
        try:
            decrypted_payload = cipher.decrypt(encrypted_payload)
            print("Decrypted Payload:", decrypted_payload)
        except Exception as e:
            print(f"Decryption failed: {e}")
            return Response(create_encrypted_response('Invalid encrypted data'), status=status.HTTP_400_BAD_REQUEST)

        if not decrypted_payload:
            return Response(create_encrypted_response('Invalid encrypted data'), status=status.HTTP_400_BAD_REQUEST)

        # Convert the decrypted payload back to a dictionary
        try:
            data = json.loads(decrypted_payload)
            print("Decrypted data as dictionary:", data)
        except json.JSONDecodeError as e:
            print(f"JSON decoding failed: {e}")
            return Response(create_encrypted_response('Invalid JSON format'), status=status.HTTP_400_BAD_REQUEST)

        # Use the decrypted data for the serializer
        serializer = UpdatePicturesSerializer(
            data=data,
            context={'user': request.user}
        )
        if not serializer.is_valid():
            first_error = next(iter(serializer.errors.values()))[0]
            return Response(create_encrypted_response(first_error), status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        response_data = {}

        if 'profile_picture' in serializer.validated_data:
            profile_picture = serializer.validated_data['profile_picture']
            ext = os.path.splitext(profile_picture.name)[1].lower()
            profile_path = f'profile/user_{user.id}{ext}'

            if user.profile_picture:
                delete_file_from_s3(str(user.profile_picture))

            presigned_url = upload_file_to_s3(
                profile_picture,
                profile_path,
                profile_picture.content_type
            )

            user.profile_picture = profile_path
            response_data['profile_url'] = presigned_url

        if 'banner_picture' in serializer.validated_data:
            banner_picture = serializer.validated_data['banner_picture']
            ext = os.path.splitext(banner_picture.name)[1].lower()
            banner_path = f'banner/user_{user.id}{ext}'

            if user.banner_picture:
                delete_file_from_s3(str(user.banner_picture))

            presigned_url = upload_file_to_s3(
                banner_picture,
                banner_path,
                banner_picture.content_type
            )

            user.banner_picture = banner_path
            response_data['banner_url'] = presigned_url

        if response_data:
            user.save()
            response_data['message'] = 'Upload successful'
            return Response(create_encrypted_response('Upload successful', response_data), status=status.HTTP_200_OK)

        return Response(create_encrypted_response('No pictures provided'), status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(f"Unexpected error: {e}")
        return Response(create_encrypted_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(method='post', **update_interests_docs)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_user_interests(request):
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

        serializer = UpdateUserInterestsSerializer(data=data)
        if not serializer.is_valid():
            first_error = next(iter(serializer.errors.values()))[0]
            return Response(create_encrypted_response(first_error), status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        serializer.update(user, serializer.validated_data)

        interest_names = user.interests.values_list('name', flat=True)
        
        response_data = {
            'interests': list(interest_names)
        }
        return Response(create_encrypted_response('Interests updated successfully', response_data), status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Unexpected error: {e}")
        return Response(create_encrypted_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(method='get', **get_suggestions_docs)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_suggested_users(request):
    try:
        suggested_users = []
        all_users = CustomUser.objects.exclude(id=request.user.id)
        
        for user in all_users:
            username = user.username.lower()  
            if username == 'next':
                suggested_users.append(user)
              
        serializer = SuggestedUserSerializer(suggested_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'message': 'Failed to get suggestions'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(method='get', **list_interests_docs)
@api_view(['GET'])
def list_interests(request):
    try:
        interests = Interest.objects.all()
        serializer = InterestSerializer(interests, many=True)
        return Response({
            'interests': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'message': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)