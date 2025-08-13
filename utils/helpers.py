from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse


def validate_exception_response_400():
    """
    common exception handler 400
    """
    return Response({'error': 'Missing Required params or invalid body', 'data': None},
    status=status.HTTP_400_BAD_REQUEST)

def validate_exception_response_404():
    """
    common exception handler 404
    """
    return Response({'error': 'Not valid route', 'data': None},
    status=status.HTTP_404_NOT_FOUND)

def validate_exception_response_403():
    """
    common exception handler 403
    """
    return Response({'error': 'Unauthorized', 'data': None},
    status=status.HTTP_403_FORBIDDEN)

def validate_exception_response_403_json():
    """
    common exception handler 403
    """
    return JsonResponse(
        {'error': 'Unauthorized', 'data': None},
        status=403
    )
