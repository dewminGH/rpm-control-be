from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models.user import User
from ..serializers.user_serializer import UpdateContainerTypeSerializer

@api_view(["PUT"])
def update_container_type(request):
    """Update a user's container_type"""
    serializer = UpdateContainerTypeSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_id = serializer.validated_data["user_id"]
    new_type = serializer.validated_data["container_type"]

    try:
        user = User.objects.get(user_id=user_id)
        user.container_type = new_type
        user.save(update_fields=["container_type"])
        return Response(
            {"message": "container_type updated successfully", "data":"successful" , 'error':None},
            status=status.HTTP_200_OK
        )
    except User.DoesNotExist:
        return Response(
            {"error": f"User with id {user_id} not found" ,'data':None},
            status=status.HTTP_404_NOT_FOUND
        )
