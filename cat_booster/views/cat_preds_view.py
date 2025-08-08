from rest_framework.decorators import  api_view 
from rest_framework.response import Response
from rest_framework import status
from utils import helpers
from ..serializers.cat_preds_serializer import CatPredsSerializer
from ..services import boot_model



@api_view(["POST"])
def cat_preds_fbv(request):
    """
    AI Predictions handler
    """
    if request.method == "POST":
        validator=CatPredsSerializer(data=request.data)
        is_valid = validator.is_valid()
        if is_valid:
            categories = ["apple", "banana", "mango", "papaya", "watermelon"]
            item_type,temperature,humidity,light,cos_2=request.data.values()
            cat_booster=boot_model.get_model()
            print(temperature)
            features = [
                temperature,
                humidity,
                light,
                cos_2,
                *[1 if item_type == cat else 0 for cat in categories]]
            print(temperature)
            print(features)
            fan_rpm = cat_booster.predict([features])
            return Response({'message': f'fan rpm {fan_rpm}'}, status=status.HTTP_200_OK)
        else:
            return helpers.validate_exception_response_400()
    return helpers.validate_exception_response_404()
