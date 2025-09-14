from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..filters.user_filter import filter_user_for_login
from utils import helpers
from ..serializers.user_serializer import UserSerializer
from rest_framework_simplejwt.tokens import AccessToken
from datetime import timedelta

@api_view(['POST'])
def login(request):
    """ Login handler """
    validator = UserSerializer(data=request.data)

    if not validator.is_valid():
        return helpers.validate_exception_response_400()

    user_name = request.data.get("user_name")
    password = request.data.get("password")
    device_sc = request.data.get("device_sc")

    res = filter_user_for_login(user_name, password, device_sc)
    user = res.first()
    print(user.user_id)
    if not user:
         return Response(
            {"message": "Username password incorrect", "data": None,},
            status=status.HTTP_200_OK
        )
    user_data = UserSerializer(user).data
    access_token = AccessToken.for_user(user)
    access_token.set_exp(from_time=None, lifetime=timedelta(days=30))
    
    if res.exists():
        user_data = UserSerializer(res.first()).data
        return Response(
            {"message": "Login successful", "data": user_data,"access_token": str(access_token),'user_id':user.user_id},
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {"message":"error","error": "Invalid username, password, or device","data": None},
            status=status.HTTP_401_UNAUTHORIZED
        )
