from rest_framework import viewsets, permissions
from .serializer import EmpresaSerializer
from .models import Empresa
from drf_spectacular.utils import extend_schema


# Create your views here.
@extend_schema(tags=["Endpoints Empresas"])
class EmpresaViewSet(viewsets.ModelViewSet):
    serializer_class = EmpresaSerializer
    queryset = Empresa.objects.all()
    