# Vista para el middleware del signup
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Empresa

import os
from django.utils import timezone

from config.supabase_client import supabase


from rest_framework import viewsets
from .serializer import RolSerializer, UsuarioSerializer
from .models import Rol, Usuario
from drf_spectacular.utils import extend_schema


# Create your views here.
@extend_schema(tags=["Endpoints rol"])
class RolViewSet(viewsets.ModelViewSet):
    serializer_class = RolSerializer
    queryset = Rol.objects.all()


@extend_schema(tags=["Endpoints Usuarios"],)
class UsuarioViewSet(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer
    queryset = Usuario.objects.all()
    
    def handle_foto(self, usuario, archivo):
        if not archivo:
            return

        nombre_archivo = f"foto_perfil/{usuario.supabase_uid}{os.path.splitext(archivo.name)[1]}"

        # Subir a Supabase (sin upsert)
        # Nota: si ya existe un archivo con ese nombre, deberías eliminarlo antes o renombrarlo
        supabase.storage.from_("images").upload(
            path=nombre_archivo,
            file=archivo.read(),
            file_options={"content-type": archivo.content_type}
        )

        # Obtener URL pública
        url_publica = supabase.storage.from_("images").get_public_url(nombre_archivo)

        # Guardar en el modelo
        usuario.foto_perfil = url_publica
        usuario.fecha_actualizacion_foto = timezone.now()
        usuario.save()

    def perform_update(self, serializer):
        usuario = serializer.save()
        archivo = self.request.FILES.get("foto")
        self.handle_foto(usuario, archivo)


# Endpoint que retorna una funcion cuyo objetivo es crear un usuario
@extend_schema(tags=["Endpoints Usuarios"], description="Este endpoint se desarrollo con el fin de registrar usuarios para el modulo de autenticación con supabase.")
@api_view(['POST'])
def signup_usuario(request):
    
    # Extraer token
    token = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    
    if not token:
        return Response({"error": "Token requerido"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Validar token con Supabase
        user_data = supabase.auth.get_user(token)
        supabase_uid = user_data.user.id
        email = user_data.user.email
        
        # Verificar si ya existe
        if Usuario.objects.filter(supabase_uid=supabase_uid).exists():
            return Response({"error": "Usuario ya existe"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener usuario que hace la petición (quien crea)
        try:
            usuario_actual = Usuario.objects.get(supabase_uid=supabase_uid)
        except Usuario.DoesNotExist:
            # Primer usuario (no existe en DB aún) - usar defaults
            usuario_actual = None
        
        # Verificar permisos para cambiar rol o empresa
        rol_id = request.data.get('rol')
        empresa_id = request.data.get('empresa')
        
        if (rol_id or empresa_id) and usuario_actual:
            if usuario_actual.rol.nombre_rol != "admin":
                return Response(
                    {"error": "Solo admin puede asignar rol/empresa diferente"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Asignar rol y empresa (default o personalizado)
        if rol_id:
            rol = Rol.objects.get(id_rol=rol_id)
        else:
            rol = Rol.objects.get(nombre_rol="driver")
        
        if empresa_id:
            empresa = Empresa.objects.get(id_empresa=empresa_id)
        else:
            empresa = Empresa.objects.get(nombre_empresa="Servientrega")
        
        # Crear usuario
        usuario = Usuario.objects.create(
            supabase_uid=supabase_uid,
            correo=email,
            nombre=request.data.get('nombre'),
            apellido=request.data.get('apellido'),
            telefono_movil=request.data.get('telefono_movil'),
            tipo_documento=request.data.get('tipo_documento', 'CC'),
            documento=request.data.get('documento'),
            rol=rol,
            empresa=empresa
        )
        
        return Response(UsuarioSerializer(usuario).data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
@extend_schema(tags=["Endpoints Usuarios"], description="Este ednpoint se desarrollo con el fin de retornar la informacion del usuario autenticado validando el token que proporciona supabase.")
@api_view(['GET'])
def usuario_actual(request):
    
    if not request.user or not isinstance(request.user, Usuario):
        return Response({"error": "No autenticado"}, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(UsuarioSerializer(request.user).data)