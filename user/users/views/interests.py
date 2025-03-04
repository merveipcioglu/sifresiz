from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema

from ..models import Interest
from ..serializers import InterestSerializer
from ..swagger import list_interests_docs

@swagger_auto_schema(method='get', **list_interests_docs)
@api_view(['GET'])
def list_interests(request):
    """List all available interests"""
    try:
        interests = Interest.objects.all().order_by('id')
        serializer = InterestSerializer(interests, many=True)
        return Response({
            'interests': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'message': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 