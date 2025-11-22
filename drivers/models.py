from django.db import models
from users.models import Usuario
from vehicles.models import Vehiculo

# Create your models here.
class Driver(models.Model):
    
    class status_driver(models.TextChoices):
        DISPONIBLE = "disponible", "Disponible"
        EN_RUTA = "en_ruta", "En ruta"
        No_DISPONIBLE = "no_disponible", "No disponible"
        
    id_conductor = models.AutoField(primary_key=True)
    conductor = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="estado_operativo")
    estado = models.CharField(choices=status_driver.choices, default=status_driver.DISPONIBLE, max_length=20)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, null=True, related_name="drivers")
    ubicacion_actual_lat = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    ubicacion_actual_lng = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    ultima_actualizacion_ubicacion = models.DateTimeField(null=True, blank=True)
    
    
    def __str__(self):
        return f"{self.conductor.nombre} - {self.estado}"
    
    class Meta:
        db_table = "estado_conductor"
