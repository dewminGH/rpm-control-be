from rest_framework import serializers
from ..models import FanRpm

class FanRpmCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FanRpm
        # "time" is auto; you don't need to send it from the client
        fields = [
            'device_secret', 'fan_speed', 'temperature',
            'humidity', 'light', 'co2', 'container_type'
        ]
