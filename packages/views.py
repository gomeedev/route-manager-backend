from rest_framework import viewsets, status, filters
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from .models import Cliente, Localidad, Paquete
from .serializer import ClienteSerializer, LocalidadSerializer, PaqueteSerializer


# Create your views here.
@extend_schema(tags=["Endpoints paquetes"])
class PaquetesViewSet(viewsets.ModelViewSet):
    serializer_class = PaqueteSerializer
    queryset = Paquete.objects.all()
    
    def update(self, request, *args, **kwargs):
        paquete = self.get_object()
        
        if paquete.estado_paquete != "Pendiente":
            return Response ({"error": f"No se puede editar un paquete en estado {paquete.estado_paquete}"}, status=status.HTTP_400_BAD_REQUEST)
            
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        paquete = self.get_object()
        
        if paquete.estado_paquete != "Pendiente":
            return Response ({"error": f"No se puede editar un paquete en estado {paquete.estado_paquete}"}, status=status.HTTP_400_BAD_REQUEST)
        return super().partial_update(request, *args, **kwargs)




@extend_schema(tags=["Endpoints clientes"])
class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    queryset = Cliente.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre", "apellido", "correo"]
    

class LocalidadViewSet(viewsets.ModelViewSet):
    serializer_class = LocalidadSerializer
    queryset = Localidad.objects.all()
    