from rest_framework import viewsets
from rest_framework.decorators import action

from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema


from .models import Vehiculo
from .serializer import VehiculoSerializer

from config.supabase_client import supabase
from django.utils import timezone
import os


# Create your views here.
@extend_schema(tags=["Endpoints Vehiculos"])
class VehiculosViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    
    
    def handle_imagen(self, vehiculo, archivo):
        
        if not archivo:
            return
        
        nombre_archivo = f"vehiculos/{vehiculo.id_vehiculo}_{timezone.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(archivo.name)[1]}"
        
        supabase.storage.from_("images").upload(
            path=nombre_archivo,
            file=archivo.read(),
            file_options={"content-type": archivo.content_type}
        )
        
        url_publica = (supabase.storage.from_("images").get_public_url(nombre_archivo))
        
        vehiculo.imagen = url_publica
        vehiculo.save()
        
        
    def perform_create(self, serializer):
        
        archivo = self.request.FILES.get("foto")
                
        if not archivo:
            raise ValidationError("Es obligatorio subir una foto del vehiculo")
        
        
        vehiculo = serializer.save()
        
        self.handle_imagen(vehiculo, archivo)
