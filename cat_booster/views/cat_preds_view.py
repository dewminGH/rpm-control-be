from rest_framework.decorators import  api_view 
from rest_framework.response import Response
from rest_framework import status
from utils import helpers
from ..serializers.cat_preds_serializer import CatPredsSerializer, GetDeviceCatPredsSerializer
from ..services import boot_model
from ..models.fan_rpm_model import FanRpm
from ..filters.rpm_filter import filter_rpm_by_device,filter_container_type



@api_view(["POST","GET"])
def cat_preds_fbv(request):
    """
    AI Predictions handler
    """
    if request.method == "POST":
        validator=CatPredsSerializer(data=request.data)
        is_valid = validator.is_valid()
        if is_valid:
            device_secret  = request.data.get("device_secret")
            cn_type = filter_container_type(device_secret).values_list("container_type", flat=True).first()
            categories = ["apple", "banana", "mango", "papaya", "watermelon"]
            # item_type,temperature,humidity,light,cos_2,device_secret,=request.data.values()
            item_type      = cn_type or request.data.get("item_type")
            temperature    = request.data.get("temperature")
            humidity       = request.data.get("humidity")
            light          = request.data.get("light")
            cos_2          = request.data.get("cos_2")
           
            cat_booster=boot_model.get_model()
            print(temperature)
            features = [
                temperature,
                humidity,
                light,
                cos_2,
                *[1 if item_type == cat else 0 for cat in categories]]
            

            # logs
            print(item_type,temperature,humidity,light,cos_2,device_secret,)
            print('feat')
            print(features)
            print('feated')

            # predict output
            fan_rpm = cat_booster.predict([features])
            # table rpm table
            insert_row_rpm_table=FanRpm(
                device_secret=device_secret,
                fan_speed=fan_rpm,
                temperature=temperature,
                humidity=humidity,
                light=light,
                co2=cos_2,
                container_type=item_type,)
            insert_row_rpm_table.save(force_insert=True)

            return Response({'data': f'fan rpm {fan_rpm}'}, status=status.HTTP_200_OK)
        else:
            print('data invalid',request.data)
            return helpers.validate_exception_response_400()
    if request.method == "GET":
       validator = GetDeviceCatPredsSerializer(data=request.query_params)
       is_valid = validator.is_valid()
       device_secret, = request.query_params.values()
       print(is_valid)
       if(is_valid):
           rpms = filter_rpm_by_device(device_secret)
           rpm_data = list(rpms.values())
           return Response({'data': {'rpm_data':rpm_data}},status=status.HTTP_200_OK)
       else:
           return helpers.validate_exception_response_400()
    return helpers.validate_exception_response_404()
