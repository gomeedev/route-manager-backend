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
            queryset = queryset.filter(estado=estado)
            return queryset


@extend_schema(tags=["Endpoints coductores"])
class DriverStateUpdateView(views.APIView):
    def patch(self, request, conductor_id):
        nuevo_estado = request.data.get("estado")

        # Validar estado
        estados_validos = [choice[0] for choice in Driver.status_driver.choices]
        if nuevo_estado not in estados_validos:
            return Response({"error": "Estado no válido"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            driver = Driver.objects.get(conductor_id=conductor_id)
        except Driver.DoesNotExist:
            return Response({"error": "Conductor no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        driver.estado = nuevo_estado
        driver.save()
        return Response({"mensaje": f"Estado actualizado a {nuevo_estado}"}, status=status.HTTP_200_OK)
