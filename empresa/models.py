import uuid
from django.db import models


# Create your models here.
class Empresa(models.Model):
    id_empresa = models.AutoField(primary_key=True)
    nit = models.CharField(max_length=30, unique=True)
    nombre_empresa = models.CharField(max_length=50, unique=True)
    telefono_empresa = models.CharField(max_length=30, unique=True)
    
    def __str__(self):
        return self.nombre_empresa
    
    class Meta:
        db_table = "empresa"
    