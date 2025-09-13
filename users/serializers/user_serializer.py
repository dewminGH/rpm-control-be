from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    """user login serializer"""

    user_name = serializers.CharField(required= True )
    password = serializers.CharField(required = True)
    device_sc = serializers.CharField(required = True)

    def create(self, validated_data: dict) -> dict:
        return validated_data

    def update(self, instance, validated_data: dict):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        return instance
    

class UpdateContainerTypeSerializer(serializers.Serializer):
    """user container type serializer"""

    user_id = serializers.IntegerField()
    container_type = serializers.CharField(max_length=50)

    def create(self, validated_data: dict) -> dict:
        return validated_data

    def update(self, instance, validated_data: dict):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        return instance
