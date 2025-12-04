from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from .models import Driver
from .serializer import DriverSerializer
from vehicles.models import Vehiculo


@extend_schema(tags=["Endpoints conductores"])
class DriverViewSet(viewsets.ModelViewSet):
    serializer_class = DriverSerializer
    queryset = Driver.objects.select_related("conductor").all()
    lookup_field = 'pk'
    
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        estado = self.request.query_params.get("estado")
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # AGREGAR ESTO: Filtrar por usuario_id
        usuario_id = self.request.query_params.get("usuario_id")
        if usuario_id:
            queryset = queryset.filter(conductor_id=usuario_id)
        
        return queryset
    
    
    @action(detail=True, methods=['post'])
    def asignar_vehiculo(self, request, pk=None):
        """
        Asigna un vehículo al conductor.
        Body: {"vehiculo": 1}
        """
        conductor = self.get_object()
        
        # Verificar que el conductor esté disponible
        if conductor.estado != "Disponible":
            return Response(
                {"error": f"No se puede asignar un conductor {conductor.estado}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        vehiculo_id = request.data.get('vehiculo')
        
        if not vehiculo_id:
            return Response(
                {"error": "Debes proporcionar el ID del vehículo"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            vehiculo = Vehiculo.objects.get(id_vehiculo=vehiculo_id)
        except Vehiculo.DoesNotExist:
            return Response(
                {"error": "Vehículo no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que el vehículo esté disponible
        if vehiculo.estado != "Disponible":
            return Response(
                {"error": f"No se puede asignar un vehiculo {vehiculo.estado}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que el vehículo no tenga conductor asignado
        if vehiculo.drivers.filter(estado__in=["Asignado", "En ruta"]).exists():
            return Response(
                {"error": "Este vehículo ya está asignado a otro conductor"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Asignar vehículo
        conductor.vehiculo = vehiculo
        conductor.save()
        
        # Cambiar estado del vehículo a Asignado
        vehiculo.estado = "Asignado"
        vehiculo.save()
        
        return Response({
            "mensaje": "Vehículo asignado correctamente",
            "vehiculo": vehiculo.placa,
            "conductor": conductor.conductor.nombre
        })
        