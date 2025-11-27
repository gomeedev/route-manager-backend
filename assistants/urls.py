from django.urls import path
from .views import consultar_asistente

urlpatterns = [
    path('consultar/', consultar_asistente, name='consultar_asistente'),
]