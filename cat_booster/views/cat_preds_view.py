from rest_framework.decorators import  api_view 
from rest_framework.response import Response
from rest_framework import status


@api_view(["GET"])
def cat_preds_fbv(request):
    if request.method == "GET":
        return Response({'message': 'xx'}, status=status.HTTP_200_OK)
    
    return Response({'error': 'Not valid route', 'data': None}, status=status.HTTP_404_NOT_FOUND)
