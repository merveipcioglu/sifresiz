import os
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

from ..serializers import UpdateUserInterestsSerializer, UpdatePicturesSerializer
from ..utils import upload_file_to_s3, delete_file_from_s3
from ..swagger import update_interests_docs, update_pictures_docs
from ..models import Interest

@swagger_auto_schema(method='post', **update_interests_docs)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_interests(request):
    try:
        serializer = UpdateInterestsSerializer(data=request.data)
        if not serializer.is_valid():
            first_error = next(iter(serializer.errors.values()))[0]
            return Response({
                'message': first_error
            }, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user.interests = ','.join(serializer.validated_data['interests'])
        user.save()

        return Response({
            'message': 'Interests updated successfully',
            'interests': serializer.validated_data['interests']
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'message': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(method='post', **update_pictures_docs)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_pictures(request):
    serializer = UpdatePicturesSerializer(
        data=request.FILES,
        context={'user': request.user}
    )
    if not serializer.is_valid():
        first_error = next(iter(serializer.errors.values()))[0]
        return Response({
            'message': first_error
        }, status=status.HTTP_400_BAD_REQUEST)

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
        return Response(response_data, status=status.HTTP_200_OK)

    return Response({
        'message': 'No pictures provided'
    }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='post', **update_interests_docs)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_user_interests(request):
    """Update user interests (maximum 3)"""
    try:
        serializer = UpdateUserInterestsSerializer(data=request.data)
        if not serializer.is_valid():
            first_error = next(iter(serializer.errors.values()))[0]
            return Response({
                'message': first_error
            }, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        serializer.update(user, serializer.validated_data)

        # Get updated interests for response
        interest_names = user.interests.values_list('name', flat=True)
        
        return Response({
            'message': 'Interests updated successfully',
            'interests': list(interest_names)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'message': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 