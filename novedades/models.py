from django.db import models
from django.db import models
from drivers.models import Driver


# Create your models here.
class Novedad(models.Model):
    class TipoNovedad(models.TextChoices):
        PROBLEMAS_ENTREGA = "problemas_entrega", "Problemas de entrega",
        PROBLEMAS_DESTINATARIO = "problemas_destinatario", "Problemas destinatario",
        PROBLEMAS_OPERATIVOS = "demoras_operativas", "Demoras operativas",
        PROBLEMAS_DOCUMENTACION = "problemas_documentacion", "Problemas documentaciòn"
        
    id_novedad = models.AutoField(unique=True)
    conductor = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="novedades")
    tipo = models.CharField(choices=TipoNovedad.choices, max_length=40)
    descripcion = models.TextField(max_length=200)
    imagen = models.URLField(blank=True, null=True)
    fecha_novedad = models.DateTimeField(blank=True, null=True, auto_now=True)
    leida = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.conductor.conductor.nombre} - {self.tipo}"
    
    class Meta:
        db_table = "novedades"
        ordering = ["-fecha_novedad"]