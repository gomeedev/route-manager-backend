from django.db import models
from vehicles.models import Vehiculo
from drivers.models import Driver

# Create your models here.
class Ruta(models.Model):
    class EstadoRuta(models.TextChoices):
        PENDIENTE = "Pendiente", "Pendiente"
        ASIGNADA = "Asignada", "Asignada"
        EN_RUTA = "En ruta", "En ruta"
        COMPLETADA = "Completada", "Completada"
        FALLIDA = "Fallida", "Fallida"
        
        
    id_ruta = models.AutoField(primary_key=True)
    estado = models.CharField(choices=EstadoRuta, default=EstadoRuta.PENDIENTE, max_length=15)
    vehiculo = models.OneToOneField(Vehiculo, on_delete=models.SET_NULL, null=True, related_name="ruta_actual")
    conductor = models.OneToOneField(Driver, on_delete=models.SET_NULL, null=True, related_name="ruta_actual")
    