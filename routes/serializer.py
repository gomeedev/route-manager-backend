from rest_framework import serializers

from django.utils import timezone

from packages.models import Paquete
from packages.serializer import PaqueteSerializer

from drivers.models import Driver
from drivers.serializer import DriverSerializer

from vehicles.models import Vehiculo
from vehicles.serializer import VehiculoSerializer

from .models import EntregaPaquete, Ruta




class EntregaPaqueteSerializer(serializers.ModelSerializer):

    paquete_info = serializers.SerializerMethodField()
    
    foto = serializers.ImageField(write_only=True, required=False)
    
    
    class Meta:
        model = EntregaPaquete
        fields = (
            "id_entrega", "paquete", "ruta", "estado", 
            "fecha_entrega", "imagen", "observacion",
            "lat_entrega", "lng_entrega", "paquete_info", "foto"
        )
        read_only_fields = ("id_entrega", "fecha_entrega", "imagen", )

 
    def get_paquete_info(self, objetoeto):
            return {
                "id": objetoeto.paquete.id_paquete,
                "direccion": objetoeto.paquete.direccion_entrega,
                "cliente": objetoeto.paquete.cliente.nombre
            }
         
   
    def validate(self, data):
            paquete = data["paquete"]
            ruta = data["ruta"]
            
            if paquete.ruta_id != ruta.id_ruta:
                raise serializers.ValidationError("El paquete no pertenece a esta ruta")
            
            if paquete.estado_paquete in ["Entregado", "Fallido"]:
                raise serializers.ValidationError("El paquete ya fue entregado")
            
            if ruta.estado != "En ruta":
                raise serializers.ValidationError("Esta ruta no esta activa")
            
            return data
    
    
    def create(self, validated_data):
        validated_data.pop('foto', None)
        entrega = super().create(validated_data)

        
        paquete = entrega.paquete
        paquete.estado_paquete = entrega.estado
        paquete.save()
        
    
        ruta = entrega.ruta
        if entrega.estado == "Entregado":
            ruta.paquetes_entregados += 1
        else:
            ruta.paquetes_fallidos += 1
        ruta.save()

        
        total_paquetes_registrados = ruta.paquetes_entregados + ruta.paquetes_fallidos
        

        if total_paquetes_registrados == ruta.total_paquetes:
            if ruta.paquetes_fallidos > ruta.paquetes_entregados:
                ruta.estado = "Fallida"
            else:
                ruta.estado = "Completada"
                
            ruta.fecha_fin = timezone.now()
            ruta.save()
            

        return entrega    
   

class RutaSerializer(serializers.ModelSerializer):
    
    conductor = serializers.PrimaryKeyRelatedField(queryset=Driver.objects.all(), write_only=True, required=False, allow_null=True)
    vehiculo = serializers.PrimaryKeyRelatedField(queryset=Vehiculo.objects.all(), write_only=True, required=False, allow_null=True)
    
    conductor_detalle = DriverSerializer(source="conductor", read_only=True)
    vehiculo_detalle = VehiculoSerializer(source="vehiculo", read_only=True)
    paquetes_asignados = PaqueteSerializer(source="paquetes", many=True, read_only=True)
    
    progreso = serializers.SerializerMethodField()
    ultima_entrega = serializers.SerializerMethodField()
    
    
    class Meta:
        model = Ruta
        fields = (
            "id_ruta", "codigo_manifiesto", "estado",
            "fecha_creacion", "fecha_inicio", "fecha_fin",
            "conductor", "conductor_detalle",
            "vehiculo", "vehiculo_detalle",
            "ruta_optimizada", "distancia_total_km", "tiempo_estimado_minutos",
            "total_paquetes", "paquetes_entregados", "paquetes_fallidos",
            "paquetes_asignados", "progreso", "ultima_entrega"
        )
        read_only_fields = (
            "id_ruta", "codigo_manifiesto", "fecha_creacion",
            "total_paquetes", "paquetes_entregados", "paquetes_fallidos"
        )
        
    
    def get_progreso(self, objeto):
        if objeto.total_paquetes == 0:
            return "0%"
        
        porcentaje = ((objeto.paquetes_entregados + objeto.paquetes_fallidos) / objeto.total_paquetes) * 100
        return f"{porcentaje:.1f}"
    
    
    def get_ultima_entrega(self, objeto):
        ultima = objeto.entregas.order_by('-fecha_entrega').first()
        
        if ultima:
            return EntregaPaqueteSerializer(ultima).data
        return None
    
    
    """ Hecho con IA """
    def validate(self, data):
        conductor = data.get('conductor')
        vehiculo = data.get('vehiculo')
        
        if conductor and Ruta.objects.filter(conductor=conductor, estado__in=["Asignada", "En ruta"]).exists():
            raise serializers.ValidationError({"conductor": "Este conductor ya tiene una ruta activa"})
        
        if vehiculo and Ruta.objects.filter(vehiculo=vehiculo, estado__in=["Asignada", "En ruta"]).exists():
            raise serializers.ValidationError({"vehiculo": "Este vehiculo ya tiene una ruta activa"})
        
        return data
    

""" Hecho con IA """
class RutaMonitoreoSerializer(serializers.ModelSerializer):
    # Ubicación en tiempo real del conductor
    conductor_ubicacion = serializers.SerializerMethodField()
    conductor_nombre = serializers.CharField(source="conductor.conductor.nombre", read_only=True)
    
    # Progreso simplificado
    progreso_porcentaje = serializers.SerializerMethodField()
    
    # Próximo paquete a entregar
    proximo_paquete = serializers.SerializerMethodField()
    
    # Paquetes pendientes (solo básico)
    paquetes_pendientes = serializers.SerializerMethodField()
    
    
    class Meta:
        model = Ruta
        fields = (
            "id_ruta", "codigo_manifiesto", "estado",
            "conductor_nombre", "conductor_ubicacion",
            "total_paquetes", "paquetes_entregados", "paquetes_fallidos",
            "progreso_porcentaje", "proximo_paquete", "paquetes_pendientes"
        )
    
    
    def get_conductor_ubicacion(self, objeto):
        if objeto.conductor:
            return {
                "lat": float(objeto.conductor.ubicacion_actual_lat) if objeto.conductor.ubicacion_actual_lat else None,
                "lng": float(objeto.conductor.ubicacion_actual_lng) if objeto.conductor.ubicacion_actual_lng else None,
                "ultima_actualizacion": objeto.conductor.ultima_actualizacion_ubicacion
            }
        return None
    
    
    def get_progreso_porcentaje(self, objeto):
        if objeto.total_paquetes == 0:
            return 0
        return round(((objeto.paquetes_entregados + objeto.paquetes_fallidos) / objeto.total_paquetes) * 100, 1)
    
    
    def get_proximo_paquete(self, objeto):
        # Obtener el paquete con menor orden_entrega que esté pendiente o en ruta
        proximo = objeto.paquetes.filter(
            estado_paquete__in=["Asignado", "En ruta"]
        ).order_by('orden_entrega').first()
        
        if proximo:
            return {
                "id": proximo.id_paquete,
                "direccion": proximo.direccion_entrega,
                "orden": proximo.orden_entrega,
                "lat": float(proximo.lat) if proximo.lat else None,
                "lng": float(proximo.lng) if proximo.lng else None
            }
        return None
    
    
    def get_paquetes_pendientes(self, objeto):
        pendientes = objeto.paquetes.filter(
            estado_paquete__in=["Asignado", "En ruta"]
        ).order_by('orden_entrega')
        
        return [
            {
                "id": p.id_paquete,
                "direccion": p.direccion_entrega,
                "orden": p.orden_entrega
            }
            for p in pendientes
        ]
        