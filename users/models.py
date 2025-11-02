import uuid
from django.db import models
from django.utils import timezone
from empresa.models import Empresa

# Create your models here.
class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.nombre_rol
    
    class Meta:
        db_table = 'rol'
    
    
class Usuario(models.Model):
    class TipoDocumento(models.TextChoices):
        CC = "CC", "Cédula de ciudadanía"
        CE = "CE", "Cédula de extranjería"
        TI = "TI", "Tarjeta de identidad"
        
    class EstadoUsuario(models.TextChoices):
        ACTIVO = "activo", "Activo"
        INACTIVO = "inactivo", "Inactivo"
    
    id_usuario = models.AutoField(primary_key=True)
    supabase_uid = models.CharField(unique=True, max_length=100)
    correo = models.EmailField(max_length=200, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    id_empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    telefono_movil = models.CharField(max_length=30)
    id_rol = models.ForeignKey(Rol, on_delete=models.PROTECT)
    tipo_documento = models.CharField(choices=TipoDocumento.choices, default=TipoDocumento.CC, max_length=30)
    documento = models.CharField(max_length=20)
    estado = models.CharField(choices=EstadoUsuario.choices, default=EstadoUsuario.ACTIVO)
    fecha_registro = models.DateTimeField(default=timezone.now)
    foto_perfil = models.ImageField(upload_to="users/profile/", blank=True, null=True)
    fecha_actualizacion_foto = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    class Meta:
        db_table = 'usuario'
    