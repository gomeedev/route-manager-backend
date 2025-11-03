from django.urls import path, include
from rest_framework import routers
from .views import RolViewSet, UsuarioViewSet, signup_usuario, usuario_actual


router = routers.DefaultRouter()

router.register(r'rol', RolViewSet, basename="rol")
router.register(r'usuario', UsuarioViewSet, basename="usuario")

urlpatterns = [
    #Endpoints para la entidad courses
    path("signup/", signup_usuario, name="signup-usuario"),
    path("usuario/me/", usuario_actual, name="usuario-actual"),
    path("", include(router.urls)),
]