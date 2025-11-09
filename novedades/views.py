from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema

from .models import Novedad
from .serializer import NovedadSerializer
from drivers.models import Driver
from users.models import Usuario

from config.supabase_client import supabase
from django.utils import timezone
import os


@extend_schema(tags=["Endpoints Novedades"])
class NovedadListCreateView(generics.ListCreateAPIView):
    
    serializer_class = NovedadSerializer
    
    def get_queryset(self):
        user = self.request.user
        print(f"Usuario: {user}, Rol: {user.rol.nombre_rol if hasattr(user, 'rol') else 'No tiene rol'}")
        
        if not isinstance(user, Usuario):
            return Novedad.objects.none()
        
        if user.rol.nombre_rol == "admin":
            return Novedad.objects.all()
        
        elif user.rol.nombre_rol == "driver":
            try:
                driver = Driver.objects.get(conductor=user)
                return Novedad.objects.filter(conductor=driver)
            except Driver.DoesNotExist:
                return Novedad.objects.none()
        return Novedad.objects.none()
    
    
    def handle_imagen(self, novedad, archivo):
        if not archivo:
            return
        
        nombre_archivo = f"novedades/{novedad.id_novedad}_{timezone.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(archivo.name)[1]}"
        
        supabase.storage.from_("images").upload(
            path=nombre_archivo,
            file=archivo.read(),
            file_options={"content-type": archivo.content_type}
        )
        
        url_publica = supabase.storage.from_("images").get_public_url(nombre_archivo)
        
        novedad.imagen = url_publica
        novedad.save()
    
    
    # ← VERIFICA QUE ESTE MÉTODO ESTÉ BIEN INDENTADO (mismo nivel que get_queryset)
    def perform_create(self, serializer):
        user = self.request.user
        
        print(f"=== PERFORM_CREATE EJECUTÁNDOSE ===")  # DEBUG
        print(f"User: {user}")
        
        # Verificar autenticación PRIMERO
        if not isinstance(user, Usuario):
            raise PermissionDenied("No autenticado")
        
        # Verificar que sea driver
        if user.rol.nombre_rol != "driver":
            raise PermissionDenied("Solo los conductores pueden crear novedades")
        
        # Obtener el driver
        try:
            driver = Driver.objects.get(conductor=user)
            print(f"Driver encontrado: {driver}")  # DEBUG
        except Driver.DoesNotExist:
            raise PermissionDenied("El usuario no es un conductor")
        
        # Guardar CON el conductor
        novedad = serializer.save(conductor=driver)
        print(f"Novedad creada: {novedad.id_novedad}")  # DEBUG
        
        # Manejar la foto
        archivo = self.request.FILES.get("foto")
        print(f"Archivo: {archivo}")  # DEBUG
        self.handle_imagen(novedad, archivo)
        
        
@extend_schema(tags=["Endpoints Novedades"])
class NovedadDetailsView(generics.RetrieveUpdateDestroyAPIView):
    
    queryset = Novedad.objects.all()
    serializer_class = NovedadSerializer
    
    
    def delete(self, request, *args, **kwargs):
        
        user = request.user
        
        if user.rol.nombre_rol != "admin":
            raise PermissionDenied("Solo el admin puede eliminar una novedad")
        return super().delete(request, *args, **kwargs)
    
    
    def patch(self, request, *args, **kwargs):
        
        user = request.user
        instance = self.get_object()
        
        if user.rol.nombre_rol != "admin":
            raise PermissionDenied("Solo el admin puede marcar la novedad como leida")
        
        leida = request.data.get("leida", None)
        if leida is not None:
            instance.leida = leida
            instance.save()
            return Response(NovedadSerializer(instance).data, status=status.HTTP_200_OK)
        
        return Response({"error": "Solo puede modificarse el campo leida"}, status=status.HTTP_400_BAD_REQUEST)
        