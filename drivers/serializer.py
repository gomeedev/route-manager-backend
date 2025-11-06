from rest_framework import serializers
from .models import Driver
from users.models import Usuario


class DriverSerializer(serializers.ModelSerializer):
    
    conductor = serializers.PrimaryKeyRelatedField(
        queryset = Usuario.objects.filter(rol__nombre_rol="driver")
    )
    
    class Meta:
        model = Driver
        fields = "__all__"
        read_only_fields = ("id_conductor",)
        
        