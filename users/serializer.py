from rest_framework import serializers
from .models import Rol, Usuario
from empresa.models import Empresa



class RolSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Rol
        fields = ("id_rol", "nombre_rol")
        read_only_fields = ("id_rol",)
        

class UsuarioSerializer(serializers.ModelSerializer):
    
    # Para reflejar la relacion - petiicones por ID
    rol = serializers.PrimaryKeyRelatedField(
        queryset = Rol.objects.all()   
    )
    empresa = serializers.PrimaryKeyRelatedField(
        queryset = Empresa.objects.all()
    )
    # Para traer todos los campos de esa entidad relacionada - para mostrar en detalles
    rol_nombre = serializers.CharField(source="rol.nombre_rol", read_only=True)
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    foto = serializers.ImageField(write_only=True, required=True)
    
    class Meta:
        model = Usuario
        fields = "__all__"
        read_only_fields = ("id_usuario", "supabase_uid", "fecha_registro", "fecha_actualizacion_foto")
        