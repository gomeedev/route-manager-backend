from drf_spectacular.utils import extend_schema

from rest_framework import generics

from drivers.models import Driver
from .serializer import NovedadSerializer

# Create your views here.
@extend_schema(tags=["Endpoints Novedades"])
class NovedadViewList(generics.ListCreateAPIView):
    queryset = Driver.objects.all()
    serializer_class = NovedadSerializer
    