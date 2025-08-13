from rest_framework import serializers

class CatPredsSerializer(serializers.Serializer):
    """
    prediction input data validate
    """
    item_type=serializers.CharField(required=True, max_length=40)
    temperature=serializers.FloatField(required=True)
    humidity=serializers.FloatField(required=True)
    light=serializers.FloatField(required=True)
    cos_2=serializers.FloatField(required=True)
    device_secret=serializers.CharField(required=True, max_length=255)

    def create(self, validated_data: dict) -> dict:
        return validated_data

    def update(self, instance, validated_data: dict):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        return instance
