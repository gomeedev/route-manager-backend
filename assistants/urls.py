from django.urls import path
from .views import consultar_asistente, example_assistant

urlpatterns = [
    path('consultar/', consultar_asistente, name='consultar_asistente'),
    path('example/', example_assistant, name="example-assistant")
]