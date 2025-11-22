from django.db import models
from django.utils import timezone

from django.utils.crypto import get_random_string

from vehicles.models import Vehiculo
from drivers.models import Driver

# Create your models here.
def generar_codigo_manifiesto():
    return f"RT-{get_random_string(8, allowed_chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"


class Ruta(models.Model):
    class EstadoRuta(models.TextChoices):
        PENDIENTE = "Pendiente", "Pendiente"
        ASIGNADA = "Asignada", "Asignada"
        EN_RUTA = "En ruta", "En ruta"
        COMPLETADA = "Completada", "Completada"
        FALLIDA = "Fallida", "Fallida"
        
        
    id_ruta = models.AutoField(primary_key=True)
    codigo_manifiesto = models.CharField(max_length=20, default=generar_codigo_manifiesto)
    
    estado = models.CharField(choices=EstadoRuta, default=EstadoRuta.PENDIENTE, max_length=15)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    
    conductor = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, related_name="rutas")
    
    ruta_optimizada = models.JSONField(null=True, blank=True)
    distancia_total_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    tiempo_estimado_minutos = models.IntegerField(null=True, blank=True)
    
    total_paquetes = models.IntegerField(default=0)
    paquetes_entregados = models.IntegerField(default=0)
    paquetes_fallidos = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.codigo_manifiesto} {self.estado}"
    
    class Meta:
        db_table = "ruta"
        ordering = ['-fecha_creacion']
        

class EntregaPaquete(models.Model):
    class EstadoEntrega(models.TextChoices):
        ENTREGADO = "Entregado", "Entregado"
        FALLIDO = "Fallido", "Fallido"
    
    id_entrega = models.AutoField(primary_key=True)
    
    """ Tuve que importar el modulo de ruta de esta manera debido a un error circular al intentar importar el modelo como normalmente se hace.
    Desconozco la razón por la que sucedio (se cree que por un error circular de importaciones) pero vi que esta era la solución y asi lo fue.
    """
    paquete = models.ForeignKey("packages.Paquete", on_delete=models.CASCADE, related_name="entregas")
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name="entregas")
    
    estado = models.CharField(choices=EstadoEntrega, max_length=10)
    fecha_entrega = models.DateTimeField(default=timezone.now)
    
    imagen = models.URLField(null=True, blank=True) 
    observacion = models.TextField(null=True, blank=True)
    
    lat_entrega = models.DecimalField(max_digits=10, decimal_places=8)
    lng_entrega = models.DecimalField(max_digits=11, decimal_places=8)
    
    class Meta:
        db_table = "entrega_paquete"