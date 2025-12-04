from rest_framework import serializers

from .models import Driver
from users.models import Usuario

from vehicles.serializer import VehiculoSerializer

from config.osm_service import OSMService




class ConductorDetalleSerializer(serializers.ModelSerializer):
    
    empresa_nombre = serializers.CharField(source="empresa.nombre_empresa", read_only=True)
    
    class Meta:
        model = Usuario
        fields = "__all__"
        
        
    
class DriverSerializer(serializers.ModelSerializer):
    
    conductor_detalle = ConductorDetalleSerializer(source="conductor", read_only=True)
    conductor = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.filter(rol__nombre_rol="driver"))
    
    vehiculo_detalle = VehiculoSerializer(source="vehiculo", read_only=True)
    
    ruta_asignada = serializers.SerializerMethodField()

    ubicacion_base = serializers.SerializerMethodField()
    
    class Meta:
        model = Driver
        fields = (
            "id_conductor", "conductor", "estado", 
            "direccion_base", "base_lat", "base_lng",
            "ubicacion_actual_lat", "ubicacion_actual_lng", "direccion_actual",
            "ultima_actualizacion_ubicacion", 
            "conductor_detalle", "vehiculo_detalle", "ruta_asignada",
            "ubicacion_base"
        )
        read_only_fields = ("id_conductor", "ubicacion_actual_lat", "ubicacion_actual_lng", "direccion_actual", "ultima_actualizacion_ubicacion")
        
    def validate(self, data):
        # Solo aplicar geocodificación si se está modificando direccion_base
        if 'direccion_base' in data and data['direccion_base']:
            direccion_completa = f"{data['direccion_base']}, Bogotá, Colombia"
            coordenadas = OSMService.geocodificar_direccion(direccion_completa)
            
            if not coordenadas:
                raise serializers.ValidationError({
                    "direccion_base": "No se pudo geocodificar la dirección. Verifica que sea correcta."
                })
            
            data['base_lat'] = coordenadas['lat']
            data['base_lng'] = coordenadas['lng']
            
        return data
    
    
    def get_ubicacion_base(self, obj):
            if obj.base_lat and obj.base_lng:
                return {
                    "direccion": obj.direccion_base or "Sin dirección base",
                    "lat": float(obj.base_lat),
                    "lng": float(obj.base_lng)
                }
            return None
    
    
    def get_ruta_asignada(self, objeto):
        ruta_activa = objeto.rutas.filter(estado__in=["Asignada", "En ruta"]).first()
        if ruta_activa:
            return ruta_activa.codigo_manifiesto
        else:
            return "Sin asignar"
    