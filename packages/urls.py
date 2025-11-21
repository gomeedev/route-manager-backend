from django.urls import path, include

from .views import ClienteViewSet, LocalidadViewSet, PaquetesViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename="cliente")
router.register(r'localidades', LocalidadViewSet, basename="localidad")
router.register(r'', PaquetesViewSet, basename="paquete")


urlpatterns = [
    path("", include(router.urls))
]