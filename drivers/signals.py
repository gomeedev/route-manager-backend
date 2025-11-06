# drivers/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import Usuario
from .models import Driver

@receiver(post_save, sender=Usuario)
def crear_estado_conductor(sender, instance, created, **kwargs):
    
    if created: #Solo cuando se crea
        if instance.rol and instance.rol.nombre_rol.lower() == "driver":
            if not hasattr(instance, "estado_operativo"):
                Driver.objects.create(conductor=instance, estado=Driver.status_driver.DISPONIBLE)