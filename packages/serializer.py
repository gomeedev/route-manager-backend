from config.osm_service import OSMService

from rest_framework import serializers
from .models import Cliente, Localidad, Barrio, Paquete


class PaqueteSerializer(serializers.ModelSerializer):
    
    paquete_asignado = serializers.SerializerMethodField()
    foto = serializers.ImageField(write_only=True, required=False)
    
    class Meta:
        model = Paquete
        fields = ("id_paquete", "fecha_registro", "fecha_entrega", "tipo_paquete", "estado_paquete", "largo", "ancho", "alto", "peso", "valor_declarado", "cantidad", "imagen", "observacion", "cliente", "barrio", "lat", "lng", "direccion_entrega", "orden_entrega", "ruta", "foto", "paquete_asignado")
        read_only_fields = ("lat", "lng", "orden_entrega", "ruta",)
        
        
    def create(self, validated_data):
        
        validated_data.pop('foto', None)
        
        direccion = validated_data["direccion_entrega"]
        barrio = validated_data["barrio"]
        localidad = barrio.id_localidad.nombre
        
        direccion_completa = f"{direccion}, {localidad}, Bogotá, Colombia"

        coordenadas = OSMService.geocodificar_direccion(direccion_completa)
    
        if coordenadas is None:
            # evidentemente el error es de geocodificación pero el mensaje es sencillo para orientar al usuario
            raise serializers.ValidationError({"direccion_entrega": "No se encontró la dirección, valida que sea valida"})
        
        validated_data['lat'] = coordenadas['lat']
        validated_data["lng"] = coordenadas["lng"]
        
        paquete = super().create(validated_data)
        
        return paquete
        
        
    def get_paquete_asignado(self, objeto):
        if objeto.ruta:
            return objeto.ruta.id_ruta
        return "Sin asignar"
   
    
    def validate_largo(self, value):
        if value <= 0:
            raise serializers.ValidationError("El campo no puede ser 0")
        return value

    def validate_ancho(self, value):
        if value <= 0:
            raise serializers.ValidationError("El campo no puede ser 0")
        return value
    
    def validate_alto(self, value):
            if value <= 0:
                raise serializers.ValidationError("El campo no puede ser 0")
            return value
        
    def validate_peso(self, value):
        if value <= 0:
            raise serializers.ValidationError("El campo no puede ser 0")
        return value
    
    
    

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = "__all__"
        
    
class LocalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Localidad
        fields = "__all__"
        

class BarrioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barrio
        fields = "__all__"
