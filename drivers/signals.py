# drivers/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from users.models import Usuario
from .models import Driver


user_roles = {"driver"}


def is_driver_role(usuario):
    if not usuario.rol:
        return False
    return usuario.rol.nombre_rol.strip().lower() in user_roles


@receiver(post_save, sender=Usuario)
def crear_estado_conductor(sender, instance, created, **kwargs):
    
    with transaction.atomic():
        try:
            driver = Driver.objects.select_for_update().get(conductor=instance)
        except Driver.DoesNotExist:
            driver = None
            
        # Si el usuario tiene rol de conductor
        if is_driver_role(instance):
            
            if not driver:
                Driver.objects.create(conductor=instance, estado_driver=Driver.status_driver.DISPONIBLE)
        else:
            if driver:
                driver.delete()
