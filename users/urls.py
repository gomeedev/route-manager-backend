from django.urls import path, include
from rest_framework import routers
from .views import RolViewSet, UsuarioViewSet


router = routers.DefaultRouter()

router.register(r'rol', RolViewSet, basename="rol")
router.register(r'usuario', UsuarioViewSet, basename="usuario")

urlpatterns = [
    #Endpoints para la entidad courses
    path("", include(router.urls))
]