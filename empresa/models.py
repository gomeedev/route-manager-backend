import uuid
from django.db import models


# Create your models here.
class Empresa(models.Model):
    id_empresa = models.UUIDField(primary_key=True, default=uuid.uuid4)
    nit = models.CharField(max_length=30)
    nombre_empresa = models.CharField(max_length=50)
    telefono_empresa = models.CharField(max_length=30)
    
    