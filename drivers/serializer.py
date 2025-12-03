from rest_framework import serializers

from .models import Driver
from users.models import Usuario

from vehicles.serializer import VehiculoSerializer


class ConductorDetalleSerializer(serializers.ModelSerializer):
    
    empresa_nombre = serializers.CharField(source="empresa.nombre_empresa", read_only=True)
    
    class Meta:
        model = Usuario
        fields = "__all__"
        
        
    
class DriverSerializer(serializers.ModelSerializer):
    
    conductor_detalle = ConductorDetalleSerializer(source="conductor", read_only=True)
    
    # Para traer el id del conductor respecto a los usuarios (su id original)
    conductor = serializers.PrimaryKeyRelatedField(
        queryset = Usuario.objects.filter(rol__nombre_rol="driver")
    )
    
    vehiculo_detalle = VehiculoSerializer(source="vehiculo", read_only=True)
    
    ruta_asignada = serializers.SerializerMethodField()
    
    class Meta:
        model = Driver
        fields = ("id_conductor", "conductor", "estado", "ubicacion_actual_lat", "ubicacion_actual_lng", "ultima_actualizacion_ubicacion", "conductor_detalle", "vehiculo_detalle", "ruta_asignada",)
        read_only_fields = ("id_conductor",)
        
        
    def get_ruta_asignada(self, objeto):
        ruta_activa = objeto.rutas.filter(estado__in=["Asignada", "En ruta"]).first()
        if ruta_activa:
            return ruta_activa.codigo_manifiesto
        else:
            return "Sin asignar"

        