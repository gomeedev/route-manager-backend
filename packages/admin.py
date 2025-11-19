from django.contrib import admin
from .models import Cliente, Localidad, Barrio, Paquete

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Paquete)
admin.site.register(Localidad)
admin.site.register(Barrio)
