from django.db import models
from django.utils import timezone


# Create your models here.
class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    direccion = models.CharField(max_length=100)
    correo = models.EmailField(max_length=50, unique=True)
    telefono_movil = models.CharField(max_length=12)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    class Meta:
        db_table = "cliente"
    

class Localidad(models.Model):
    class LocalidadChoices(models.TextChoices):
        USAQUEN = "Usaquén", "Usaquén"
        CHAPINERO = "Chapinero", "Chapinero"
        SANTA_FE = "Santa Fe", "Santa Fe"
        SAN_CRISTOBAL = "San Cristóbal", "San Cristóbal"
        USME = "Usme", "Usme"
        TUNJUELITO = "Tunjuelito", "Tunjuelito"
        BOSA = "Bosa", "Bosa"
        KENNEDY = "Kennedy", "Kennedy"
        FONTIBON = "Fontibón", "Fontibón"
        ENGATIVA = "Engativá", "Engativá"
        SUBA = "Suba", "Suba"
        BARRIOS_UNIDOS = "Barrios Unidos", "Barrios Unidos"
        TEUSAQUILLO = "Teusaquillo", "Teusaquillo"
        MARTIRES = "Los Mártires", "Los Mártires"
        ANTONIO_NARINO = "Antonio Nariño", "Antonio Nariño"
        PUENTE_ARANDA = "Puente Aranda", "Puente Aranda"
        CANDELARIA = "La Candelaria", "La Candelaria"
        RAFAEL_URIBE = "Rafael Uribe Uribe", "Rafael Uribe Uribe"
        CIUDAD_BOLIVAR = "Ciudad Bolívar", "Ciudad Bolívar"
        SUMAPAZ = "Sumapaz", "Sumapaz"
        
    id_localidad = models.AutoField(primary_key=True)
    nombre = models.CharField(choices=LocalidadChoices, max_length=50, unique=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = "localidad"
    
    
class Paquete(models.Model):
    class EstadoPaquete(models.TextChoices):
        PENDIENTE = "Pendiente", "Pendiente"
        ASIGNADO = "Asignado", "Asignado"
        EN_RUTA = "En ruta", "En ruta"
        ENTREGADO = "Entregado", "Entregado"
        FALLIDO = "Fallido", "Fallido"
        
    class TipoPaquete(models.TextChoices):
        GRANDE = "Grande", "Grande"
        MEDIANO = "Mediano", "Mediano"
        PEQUENO = "Pequeno", "Pequeño"
        REFRIGERADO = "Refrigerado", "Refrigerado"
        FRAGIL = "Fragil", "Fragil"
    
    id_paquete = models.AutoField(primary_key=True)
    fecha_registro = models.DateTimeField(default=timezone.now)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    tipo_paquete = models.CharField(choices=TipoPaquete, default=TipoPaquete.MEDIANO, max_length=15)
    estado_paquete = models.CharField(choices=EstadoPaquete, default=EstadoPaquete.PENDIENTE, max_length=12)
    largo = models.FloatField()
    ancho = models.FloatField()
    alto = models.FloatField()
    peso = models.FloatField()
    valor_declarado = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="paquetes")
    localidad = models.ForeignKey(Localidad, on_delete=models.PROTECT, default=None)
    
    # Google Maps
    lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    lng = models.DecimalField(max_digits=11, decimal_places=7, null=True, blank=True) 
    direccion_entrega = models.CharField(max_length=200)
    orden_entrega = models.IntegerField(null=True, blank=True)
    
    """ Tuve que importar el modulo de ruta de esta manera debido a un error circular al intentar importar el modelo como normalmente se hace.
    Desconozco la razón por la que sucedio (se cree que por un error circular de importaciones) pero vi que esta era la solución y asi lo fue.
    """
    ruta = models.ForeignKey("routes.Ruta", on_delete=models.SET_NULL, null=True, blank=True, related_name="paquetes")
    
    def __str__(self):
        return f"{self.tipo_paquete} {self.estado_paquete}"
    
    class Meta:
        db_table = "paquete"
