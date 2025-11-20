from rest_framework import status, views, generics
from rest_framework.response import Response
from .models import Driver
from .serializer import DriverSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample


# Create your views here.

@extend_schema(tags=["Endpoints coductores"])
class DriverListView(generics.ListAPIView):
    serializer_class = DriverSerializer
    
    def get_queryset(self):
        queryset = Driver.objects.select_related("conductor").all()
        
        estado = self.request.query_params.get("estado")
        if estado:
            return queryset.filter(estado=estado)
        return queryset
        

@extend_schema(tags=["Endpoints coductores"])
class DriverDetailView(generics.RetrieveUpdateAPIView):
    
    # Ver y editar info completa del conductor
    serializer_class = DriverSerializer
    lookup_field = 'id_conductor'
    queryset = Driver.objects.select_related("conductor").all()
    
    def update(self, request, *args, **kwargs):
        driver = self.get_object()
        
        # Actualizar datos del conductor (Usuario)
        conductor_data = request.data.get('conductor_detalle', {})
        if conductor_data:
            for key, value in conductor_data.items():
                setattr(driver.conductor, key, value)
            driver.conductor.save()
        
        # Actualizar estado operativo
        if 'estado' in request.data:
            driver.estado = request.data['estado']
            driver.save()
        
        serializer = self.get_serializer(driver)
        return Response(serializer.data)
