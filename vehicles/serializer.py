from rest_framework import serializers
from routes.models import Ruta
from .models import Vehiculo
from empresa.models import Empresa


class VehiculoSerializer(serializers.ModelSerializer):
    
    ruta_asignada = serializers.SerializerMethodField()
    foto = serializers.ImageField(write_only=True, required=True)
    
    
    class Meta:
        model = Vehiculo
        fields = ("id_vehiculo", "tipo", "placa", "imagen", "estado", "ruta_asignada", "foto")
        read_only_fields = ("id_vehiculo", "imagen")
        

    def create(self, validated_data):

        validated_data.pop('foto', None)
        return super().create(validated_data)
    
    
    def get_ruta_asignada(self, objeto):
        ruta_activa = objeto.rutas.filter(estado__in=["Asignada", "En ruta"]).first()
        return ruta_activa.id_ruta if ruta_activa else "Sin asignar"
        