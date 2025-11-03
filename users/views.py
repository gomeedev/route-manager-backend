from rest_framework import viewsets
from .serializer import RolSerializer, UsuarioSerializer
from .models import Rol, Usuario
from drf_spectacular.utils import extend_schema


# Create your views here.
@extend_schema(tags=["Endpoints rol"])
class RolViewSet(viewsets.ModelViewSet):
    serializer_class = RolSerializer
    queryset = Rol.objects.all()


@extend_schema(tags=["Endpoints Usuarios"])
class UsuarioViewSet(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer
    queryset = Usuario.objects.all()