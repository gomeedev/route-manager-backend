from config.osm_service import OSMService

from rest_framework import serializers
from .models import Cliente, Localidad, Paquete




class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = "__all__"
        
    
class LocalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Localidad
        fields = "__all__"
        
        
class PaqueteSerializer(serializers.ModelSerializer):
    
    cliente = serializers.PrimaryKeyRelatedField(queryset = Cliente.objects.all(), write_only=True)
    localidad = serializers.PrimaryKeyRelatedField(queryset = Localidad.objects.all(), write_only=True)
    
    cliente_detalle = ClienteSerializer(source="cliente", read_only=True)
    localidad_detalle = LocalidadSerializer(source="localidad", read_only=True)
    
    paquete_asignado = serializers.SerializerMethodField()
    
    ultimo_intento_entrega = serializers.SerializerMethodField()
    
    
    class Meta:
        model = Paquete
        fields = ("id_paquete", "fecha_registro", "fecha_entrega", "tipo_paquete", "estado_paquete", "largo", "ancho", "alto", "peso", "valor_declarado", "cantidad", "cliente", "cliente_detalle", "localidad", "localidad_detalle", "destinatario_nombre", "destinatario_apellido", "destinatario_telefono", "destinatario_correo", "lat", "lng", "direccion_entrega", "orden_entrega", "ruta", "paquete_asignado", "ultimo_intento_entrega", )
        read_only_fields = ("lat", "lng", "orden_entrega", "ruta", )
        
        
    def create(self, validated_data):
        
        direccion = validated_data["direccion_entrega"]
        localidad = validated_data["localidad"]
        
        direccion_completa = f"{direccion}, {localidad.nombre}, Bogotá, Colombia"

        coordenadas = OSMService.geocodificar_direccion(direccion_completa)
    
        if coordenadas is None:
            # evidentemente el error es de geocodificación pero el mensaje es sencillo para orientar al usuario
            raise serializers.ValidationError({"direccion_entrega": "No se encontró la dirección, valida que sea valida"})
        
        validated_data['lat'] = coordenadas['lat']
        validated_data["lng"] = coordenadas["lng"]
        
        paquete = super().create(validated_data)

        return paquete
    
    
    def update(self, instance, validated_data):
        
        direccion = validated_data["direccion_entrega"]
        localidad = validated_data.get("localidad", instance.localidad)
        
        if direccion:  # Solo si envían nueva dirección
            direccion_completa = f"{direccion}, {localidad.nombre}, Bogotá, Colombia"
        
        coordenadas = OSMService.geocodificar_direccion(direccion_completa)
    
        if coordenadas is None:
            # evidentemente el error es de geocodificación pero el mensaje es sencillo para orientar al usuario
            raise serializers.ValidationError({"direccion_entrega": "No se encontró la dirección, valida que sea valida"})
        
        validated_data['lat'] = coordenadas['lat']
        validated_data["lng"] = coordenadas["lng"]
        
        paquete = super().update(instance, validated_data)
        
        return paquete

        
    def get_paquete_asignado(self, objeto):
        if objeto.ruta:
            return objeto.ruta.codigo_manifiesto
        else:
            return "Sin asignar"
        
        
    def get_ultimo_intento_entrega(self, obj):
        ultimo = obj.entregas.order_by('-fecha_entrega').first()
        if ultimo:
            return {
                "estado": ultimo.estado,
                "fecha": ultimo.fecha_entrega,
                "imagen": ultimo.imagen,
                "observacion": ultimo.observacion
            }
        return None
   

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
