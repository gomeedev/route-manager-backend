from rest_framework import viewsets

from drf_spectacular.utils import extend_schema

from .models import Cliente, Localidad, Paquete
from .serializer import ClienteSerializer, LocalidadSerializer, PaqueteSerializer


# Create your views here.
@extend_schema(tags=["Endpoints paquetes"])
class PaquetesViewSet(viewsets.ModelViewSet):
    serializer_class = PaqueteSerializer
    queryset = Paquete.objects.all()


@extend_schema(tags=["Endpoints clientes"])
class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    queryset = Cliente.objects.all()
    

class LocalidadViewSet(viewsets.ModelViewSet):
    serializer_class = LocalidadSerializer
    queryset = Localidad.objects.all()
    