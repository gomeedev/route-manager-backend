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

    
class ConductorDetalleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            "nombre", "apellido", "telefono_movil",
            "tipo_documento", "documento", "correo", "estado"
        ]

    def validate_correo(self, value):
        usuario = self.instance  # puede ser None si no le asignamos instancia

        # Si tenemos instancia y el correo no cambió, permitirlo
        if usuario and usuario.correo == value:
            return value

        # Verificar unicidad excluyendo al propio usuario (usar pk es más robusto)
        if Usuario.objects.filter(correo=value).exclude(pk=getattr(usuario, "pk", None)).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")

        return value

 
        
    
class DriverSerializer(serializers.ModelSerializer):
    
    conductor_detalle = ConductorDetalleSerializer(source="conductor", read_only=True)
    conductor_update = ConductorDetalleUpdateSerializer(source="conductor", write_only=True, required=False)
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
            "conductor_detalle", "vehiculo_detalle", "conductor_update", "ruta_asignada",
            "ubicacion_base"
        )
        read_only_fields = ("id_conduc1tor", "ubicacion_actual_lat", "ubicacion_actual_lng", "direccion_actual", "ultima_actualizacion_ubicacion")
        
    
    def __init__(self, *args, **kwargs):
        """
        Cuando el serializer padre se instancia con una instancia de Driver,
        asignamos la instancia del usuario al serializer anidado para que
        validaciones como validate_correo puedan comparar correctamente.
        """
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            # instance puede ser un Driver o una lista (cuando many=True)
            driver_instance = self.instance
            # Si many=True self.instance es una lista/querset: no aplicamos
            if not isinstance(driver_instance, (list, tuple, set)):
                try:
                    usuario_instance = driver_instance.conductor
                    # asignar la instancia al serializer anidado si existe el campo
                    if "conductor_update" in self.fields:
                        self.fields["conductor_update"].instance = usuario_instance
                except Exception:
                    pass
        
        
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
          
            
        if self.instance and self.instance.estado in ["En ruta", "Asignado"]:
            if 'vehiculo' in data and data['vehiculo'] != self.instance.vehiculo:
                raise serializers.ValidationError({
                    "vehiculo": f"No se puede cambiar el vehículo mientras el conductor está {self.instance.estado}"
                })
            
        return data
    
    
    
    def update(self, instance, validated_data):
        """
        Aplicar manualmente los cambios al Usuario relacionado (si vienen)
        y luego actualizar el Driver.
        Nota: validated_data contendrá la clave 'conductor' por el source="conductor".
        """
        # 1) extraer datos del usuario (si llegaron)
        usuario_data = validated_data.pop("conductor", None)
        
        instance = super().update(instance, validated_data)

        if usuario_data:
            usuario = instance.conductor
            for campo, valor in usuario_data.items():
                setattr(usuario, campo, valor)
            usuario.save()

        return instance
    
    
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
    