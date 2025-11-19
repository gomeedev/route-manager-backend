from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from drf_spectacular.utils import extend_schema

from config.supabase_client import supabase
from django.utils import timezone
import os

from .models import Cliente, Localidad, Barrio, Paquete
from .serializer import ClienteSerializer, LocalidadSerializer, BarrioSerializer, PaqueteSerializer


# Create your views here.
@extend_schema(tags=["Endpoints paquetes"])
class PaquetesViewSet(viewsets.ModelViewSet):
    serializer_class = PaqueteSerializer
    queryset = Paquete.objects.all()
    
    
    def handle_imagen(self, paquete, archivo):
        
        if not archivo:
            return
        
        nombre_archivo = f"paquetes/{paquete.id_paquete}_{timezone.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(archivo.name)[1]}"
        
        supabase.storage.from_("images").upload(
            path=nombre_archivo,
            file=archivo.read(),
            file_options={"content-type": archivo.content_type}
        )

        url_publica = (supabase.storage.from_("images").get_public_url(nombre_archivo))
        
        paquete.imagen = url_publica
        paquete.save()
    
    
    def perform_create(self, serializer):
        archivo = self.request.FILES.get("foto")
        paquete = serializer.save()
        
        self.handle_imagen(paquete, archivo)
        



class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    queryset = Cliente.objects.all()
    
    
class LocalidadViewSet(viewsets.ModelViewSet):
    serializer_class = LocalidadSerializer
    queryset = Localidad.objects.all()
    
    
class BarrioViewSet(viewsets.ModelViewSet):
    serializer_class = BarrioSerializer
    queryset = Barrio.objects.all()