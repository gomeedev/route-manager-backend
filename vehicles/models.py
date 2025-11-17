from django.db import models


# Create your models here.
class Vehiculo(models.Model):
    class TipoVehiculo(models.TextChoices):
        CAMION = "Camion", "Camión"
        FURGON = "Furgon", "Furgón"
        CAMIONETA = "Camioneta", "Camioneta"
        MOTO = "Moto", "Moto"
        
    class EstadoVehiculo(models.TextChoices):
        DISPONIBLE = "Disponible", "Disponible"
        EN_RUTA = "En ruta", "En ruta"
        NO_DISPONIBLE = "No disponible", "No disponible"
        
    
    id_vehiculo = models.AutoField(primary_key=True)
    tipo = models.CharField(choices=TipoVehiculo, default=TipoVehiculo.FURGON, max_length=10)
    placa = models.CharField(max_length=10, unique=True)
    imagen = models.URLField(null=False, blank=False)
    estado = models.CharField(choices=EstadoVehiculo, default=EstadoVehiculo.DISPONIBLE, max_length=15)
    
    
    def __str__(self):
        return f"{self.placa} {self.tipo}"
    
    class Meta:
        db_table = "vehiculo"