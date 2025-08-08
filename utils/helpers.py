from rest_framework.response import Response 
from rest_framework import status


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
