from django.db import models
from users.models import Usuario

# Create your models here.
class Driver(models.Model):
    
    class status_driver(models.TextChoices):
        DISPONIBLE = "disponible", "Disponible"
        EN_RUTA = "en_ruta", "En ruta"
        No_DISPONIBLE = "no_disponible", "No disponible"
        
    id_conductor = models.AutoField(primary_key=True)
    conductor = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="estado_operativo")
    estado = models.CharField(choices=status_driver.choices, default=status_driver.DISPONIBLE, max_length=20)
    
    
    def __str__(self):
        return f"{self.conductor.nombre} - {self.estado}"
    
    class Meta:
        db_table = "estado_conductor"
