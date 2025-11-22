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


@extend_schema(tags=["Endpoints coductores"])
class DriverStateUpdateView(views.APIView):
    def patch(self, request, id_conductor):
        nuevo_estado = request.data.get("estado")

        # Validar estado
        estados_validos = [choice[0] for choice in Driver.status_driver.choices]
        if nuevo_estado not in estados_validos:
            return Response({"error": "Estado no válido"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            driver = Driver.objects.get(id_conductor=id_conductor)
        except Driver.DoesNotExist:
            return Response({"error": "Conductor no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        driver.estado = nuevo_estado
        driver.save()
        return Response({"mensaje": f"Estado actualizado a {nuevo_estado}"}, status=status.HTTP_200_OK)