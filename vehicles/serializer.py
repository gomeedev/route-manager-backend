from rest_framework import serializers
from routes.models import Ruta
from .models import Vehiculo
from empresa.models import Empresa


class VehiculoSerializer(serializers.ModelSerializer):
    
    conductor_asignado = serializers.SerializerMethodField()
    foto = serializers.ImageField(write_only=True, required=True)
    
    
    class Meta:
        model = Vehiculo
        fields = ("id_vehiculo", "tipo", "placa", "imagen", "estado", "conductor_asignado", "foto")
        read_only_fields = ("id_vehiculo", "imagen")
        

    def create(self, validated_data):

        validated_data.pop('foto', None)
        return super().create(validated_data)
    
    
    def update(self, instance, validated_data):
        
        validated_data.pop('foto', None)
        return super().update(instance, validated_data)
    
    
    def get_conductor_asignado(self, objeto):
        conductor_activo = objeto.drivers.filter(estado__in=["Disponible", "Asignado"]).first()
        if conductor_activo:
            return conductor_activo.id_conductor
        else:
            return "Sin asignar"

