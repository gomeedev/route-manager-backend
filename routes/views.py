# routes/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction

from drf_spectacular.utils import extend_schema

import os
from config.supabase_client import supabase
from supabase import create_client

from .models import Ruta, EntregaPaquete
from .serializer import RutaSerializer, RutaMonitoreoSerializer, EntregaPaqueteSerializer
from packages.models import Paquete
from drivers.models import Driver
from vehicles.models import Vehiculo


"""Hecho casi completamente por IA"""
@extend_schema(tags=["Endpoints rutas"])
class RutaViewSet(viewsets.ModelViewSet):
    serializer_class = RutaSerializer
    queryset = Ruta.objects.select_related('conductor', 'vehiculo').prefetch_related('paquetes').all()
    
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por estado
        estado = self.request.query_params.get('estado')
        if estado:
            return queryset.filter(estado=estado)
        
        return queryset
    
    
    def handle_imagen(self, entrega, archivo):
        if not archivo:
            return
        
        nombre_archivo = f"entregas/{entrega.id_entrega}_{timezone.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(archivo.name)[1]}"
        
        supabase.storage.from_("images").upload(
            path=nombre_archivo,
            file=archivo.read(),
            file_options={"content-type": archivo.content_type}
        )
        
        url_publica = (supabase.storage.from_("images").get_public_url(nombre_archivo))
        
        entrega.imagen = url_publica
        entrega.save()
        
    
    @action(detail=True, methods=['post'])
    def asignar_paquetes(self, request, pk=None):
        """
        Asigna paquetes a una ruta.
        Body: {"paquetes": [1, 2, 3, 4]}
        """
        ruta = self.get_object()
        
        if ruta.estado not in ["Pendiente", "Asignada"]:
            return Response(
                {"error": "Solo puedes asignar paquetes a rutas Pendientes o Asignadas"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        paquetes_ids = request.data.get('paquetes', [])
        
        if not paquetes_ids:
            return Response(
                {"error": "Debes proporcionar al menos un paquete"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que todos los paquetes existen y están disponibles
        paquetes = Paquete.objects.filter(id_paquete__in=paquetes_ids)
        
        if paquetes.count() != len(paquetes_ids):
            return Response(
                {"error": "Algunos paquetes no existen"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que estén disponibles (Pendiente)
        no_disponibles = paquetes.exclude(estado_paquete="Pendiente")
        if no_disponibles.exists():
            return Response(
                {"error": f"Los paquetes {list(no_disponibles.values_list('id_paquete', flat=True))} no están disponibles"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Asignar paquetes
        with transaction.atomic():
            paquetes.update(
                ruta=ruta,
                estado_paquete="Asignado"
            )
            
            # Actualizar contador
            ruta.total_paquetes = ruta.paquetes.count()
            ruta.estado = "Asignada"
            ruta.save()
        
        return Response({
            "mensaje": f"{paquetes.count()} paquetes asignados correctamente",
            "total_paquetes": ruta.total_paquetes
        })
        
    
    @action(detail=True, methods=['post'])
    def asignar_conductor(self, request, pk=None):
        """
        Asigna un conductor a la ruta.
        Body: {"conductor": 1}
        """
        ruta = self.get_object()
        
        if ruta.estado not in ["Pendiente", "Asignada"]:
            return Response(
                {"error": "Solo puedes asignar conductores a rutas Pendientes o Asignadas"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conductor_id = request.data.get('conductor')
        
        if not conductor_id:
            return Response(
                {"error": "Debes proporcionar el ID del conductor"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conductor = Driver.objects.get(id_conductor=conductor_id)
        except Driver.DoesNotExist:
            return Response(
                {"error": "Conductor no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que el conductor esté disponible
        if conductor.estado != "disponible":
            return Response(
                {"error": f"El conductor está {conductor.estado}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que no tenga ruta activa
        if Ruta.objects.filter(
            conductor=conductor,
            estado__in=["Asignada", "En ruta"]
        ).exists():
            return Response(
                {"error": "Este conductor ya tiene una ruta activa"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Asignar conductor
        ruta.conductor = conductor
        ruta.save()
        
        return Response({
            "mensaje": "Conductor asignado correctamente",
            "conductor": conductor.conductor.nombre,
            "ruta": ruta.codigo_manifiesto
        })


    @action(detail=True, methods=['post'])
    def asignar_vehiculo(self, request, pk=None):
        """
        Asigna un vehículo a la ruta.
        Body: {"vehiculo": 1}
        """
        ruta = self.get_object()
        
        if ruta.estado not in ["Pendiente", "Asignada"]:
            return Response(
                {"error": "Solo puedes asignar vehículos a rutas Pendientes o Asignadas"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        vehiculo_id = request.data.get('vehiculo')
        
        if not vehiculo_id:
            return Response(
                {"error": "Debes proporcionar el ID del vehículo"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            vehiculo = Vehiculo.objects.get(id_vehiculo=vehiculo_id)
        except Vehiculo.DoesNotExist:
            return Response(
                {"error": "Vehículo no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que el vehículo esté disponible
        if vehiculo.estado != "Disponible":
            return Response(
                {"error": f"El vehículo está {vehiculo.estado}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que no tenga ruta activa
        if Ruta.objects.filter(
            vehiculo=vehiculo,
            estado__in=["Asignada", "En ruta"]
        ).exists():
            return Response(
                {"error": "Este vehículo ya está en uso"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Asignar vehículo
        ruta.vehiculo = vehiculo
        ruta.save()
        
        return Response({
            "mensaje": "Vehículo asignado correctamente",
            "vehiculo": vehiculo.placa,
            "ruta": ruta.codigo_manifiesto
        })
    
    
    @action(detail=True, methods=['post'])
    def calcular_ruta(self, request, pk=None):
        """
        Calcula la ruta optimizada usando OSRM.
        Guarda polyline, distancia y tiempo estimado.
        """
        ruta = self.get_object()
        
        if ruta.total_paquetes == 0:
            return Response(
                {"error": "No hay paquetes asignados a esta ruta"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener paquetes ordenados
        paquetes = ruta.paquetes.all().order_by('id_paquete')
        
        # Extraer coordenadas
        coordenadas = []
        for paquete in paquetes:
            if not paquete.lat or not paquete.lng:
                return Response(
                    {"error": f"El paquete {paquete.id_paquete} no tiene coordenadas"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            coordenadas.append((float(paquete.lat), float(paquete.lng)))
        
        # Llamar a OSRM
        resultado = OSMService.calcular_ruta_optimizada(coordenadas)
        
        if not resultado:
            return Response(
                {"error": "No se pudo calcular la ruta. Verifica las coordenadas."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Guardar resultado
        with transaction.atomic():
            ruta.ruta_optimizada = {
                "polyline": resultado['polyline'],
                "geometry": resultado['geometry'],
                "orden": resultado['orden']
            }
            ruta.distancia_total_km = resultado['distancia_km']
            ruta.tiempo_estimado_minutos = resultado['duracion_minutos']
            ruta.save()
            
            # Asignar orden de entrega según resultado de OSRM
            for idx, paquete_idx in enumerate(resultado['orden'], start=1):
                paquete = paquetes[paquete_idx]
                paquete.orden_entrega = idx
                paquete.save()
        
        return Response({
            "mensaje": "Ruta calculada correctamente",
            "distancia_km": ruta.distancia_total_km,
            "tiempo_estimado_minutos": ruta.tiempo_estimado_minutos,
            "orden_paquetes": [paquetes[i].id_paquete for i in resultado['orden']],
            "geometry": resultado['geometry']  # Para dibujar en el mapa
        })

    
    
    @action(detail=True, methods=['post'])
    def iniciar_ruta(self, request, pk=None):
        """
        Inicia la ruta: cambia estados y activa la simulación.
        """
        ruta = self.get_object()
        
        if ruta.estado != "Asignada":
            return Response(
                {"error": "Solo puedes iniciar rutas en estado Asignada"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not ruta.ruta_optimizada:
            return Response(
                {"error": "Debes calcular la ruta antes de iniciarla"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Cambiar estado de ruta
            ruta.estado = "En ruta"
            ruta.fecha_inicio = timezone.now()
            ruta.save()
            
            # Cambiar estado de paquetes
            ruta.paquetes.update(estado_paquete="En ruta")
            
            # Cambiar estado del conductor
            if ruta.conductor:
                ruta.conductor.estado = "en_ruta"
                ruta.conductor.save()
            
            # Cambiar estado del vehículo
            if ruta.vehiculo:
                ruta.vehiculo.estado = "En ruta"
                ruta.vehiculo.save()
        
        return Response({
            "mensaje": "Ruta iniciada correctamente",
            "fecha_inicio": ruta.fecha_inicio,
            "polyline": ruta.ruta_optimizada.get("polyline")
        })
    
    
    @action(detail=True, methods=['post'])
    def actualizar_ubicacion(self, request, pk=None):
        """
        Driver envía su ubicación actual durante la simulación.
        Body: {"lat": 4.123, "lng": -74.456}
        """
        ruta = self.get_object()
        
        if ruta.estado != "En ruta":
            return Response(
                {"error": "Solo puedes actualizar ubicación en rutas activas"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lat = request.data.get('lat')
        lng = request.data.get('lng')
        
        if not lat or not lng:
            return Response(
                {"error": "Debes proporcionar lat y lng"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar ubicación del conductor
        if ruta.conductor:
            ruta.conductor.ubicacion_actual_lat = lat
            ruta.conductor.ubicacion_actual_lng = lng
            ruta.conductor.ultima_actualizacion_ubicacion = timezone.now()
            ruta.conductor.save()
        
        return Response({"mensaje": "Ubicación actualizada"})
    
    
    @action(detail=True, methods=['post'])
    def marcar_entrega(self, request, pk=None):
        """
        Driver marca un paquete como entregado o fallido.
        Body: {
            "paquete": 1,
            "estado": "Entregado",
            "imagen": "https://...",
            "observacion": "Cliente recibió conforme",
            "lat": 4.123,
            "lng": -74.456
        }
        """
        ruta = self.get_object()
        
        if ruta.estado != "En ruta":
            return Response(
                {"error": "Solo puedes marcar entregas en rutas activas"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        archivo = request.FILES.get("foto")
        
        # Crear registro de entrega
        data = {
            **request.data,
            "ruta": ruta.id_ruta
        }
        
        serializer = EntregaPaqueteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        entrega = serializer.save()
        
        self.handle_imagen(entrega, archivo)
        
        return Response({
            "mensaje": "Entrega registrada correctamente",
            "imagen": entrega.imagen,
            "progreso": f"{ruta.paquetes_entregados + ruta.paquetes_fallidos}/{ruta.total_paquetes}"
        })
    
    
    @action(detail=True, methods=['get'])
    def monitorear(self, request, pk=None):
        """
        Admin consulta el estado actual de la ruta (polling).
        Retorna ubicación del conductor, progreso, próximo paquete.
        """
        ruta = self.get_object()
        serializer = RutaMonitoreoSerializer(ruta)
        return Response(serializer.data)
    
    
    @action(detail=True, methods=['post'])
    def cerrar_ruta(self, request, pk=None):
        """
        Cierra manualmente una ruta (opcional, también se cierra automáticamente).
        """
        ruta = self.get_object()
        
        if ruta.estado not in ["En ruta", "Asignada"]:
            return Response(
                {"error": "Solo puedes cerrar rutas activas"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Determinar estado final
            if ruta.paquetes_fallidos > ruta.paquetes_entregados:
                ruta.estado = "Fallida"
            else:
                ruta.estado = "Completada"
            
            ruta.fecha_fin = timezone.now()
            ruta.save()
            
            # Liberar conductor
            if ruta.conductor:
                ruta.conductor.estado = "disponible"
                ruta.conductor.save()
            
            # Liberar vehículo
            if ruta.vehiculo:
                ruta.vehiculo.estado = "Disponible"
                ruta.vehiculo.save()
        
        return Response({
            "mensaje": f"Ruta cerrada con estado: {ruta.estado}",
            "entregados": ruta.paquetes_entregados,
            "fallidos": ruta.paquetes_fallidos
        })
