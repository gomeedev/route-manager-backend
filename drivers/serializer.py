from rest_framework import serializers
from .models import Driver
from users.models import Usuario


class ConductorDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = "__all__"
        
        
    
class DriverSerializer(serializers.ModelSerializer):
    
    conductor_detalle = ConductorDetalleSerializer(source="conductor", read_only=True)
    
    conductor = serializers.PrimaryKeyRelatedField(
        queryset = Usuario.objects.filter(rol__nombre_rol="driver")
    )
    
    class Meta:
        model = Driver
        fields = "__all__"
        read_only_fields = ("id_conductor",)
        
        