from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import VehiculosViewSet


router = DefaultRouter()
router.register(r'', VehiculosViewSet, basename='vehiculo')

urlpatterns = [
    path("", include(router.urls))
]