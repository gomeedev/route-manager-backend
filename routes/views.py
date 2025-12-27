# routes/views.py
from django.http import HttpResponse

import requests

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction

from drf_spectacular.utils import extend_schema

from config.supabase_client import supabase
from django.utils import timezone
import os

from config.osm_service import OSMService

from .models import Ruta, EntregaPaquete
from .serializer import RutaSerializer, RutaMonitoreoSerializer, EntregaPaqueteSerializer
from packages.models import Paquete
from packages.serializer import PaqueteSerializer
from drivers.models import Driver
from vehicles.models import Vehiculo

from .pdf import generar_pdf_ruta
from .utils import haversine_distance_vectorized




"""Desarrollado en su mayoria con AI"""
@extend_schema(tags=["Endpoints rutas"])
class RutaViewSet(viewsets.ModelViewSet):
    serializer_class = RutaSerializer
    queryset = Ruta.objects.select_related('conductor').prefetch_related('paquetes').all()
    
    
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
        
        if ruta.estado != "Pendiente":
            return Response(
                {"error": "Solo puedes asignar paquetes a rutas Pendientes"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        paquetes_ids = request.data.get('paquetes', [])
        
        if not paquetes_ids:
            return Response(
                {"error": "Debes proporcionar al menos un paquete"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        print("DEBUG asignar_paquetes: paquetes_ids =", paquetes_ids)
        
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
        
        # Asignar paquetes y actualizar contador en una sola transacción
        with transaction.atomic():
            # Actualizar los paquetes
            paquetes.update(
                ruta=ruta,
                estado_paquete="Asignado"
            )
            
            # Usar el len() de la lista original en lugar de hacer un .count()
            # Esto evita problemas de caché y asegura la precisión
            ruta.total_paquetes = ruta.total_paquetes + len(paquetes_ids)
            ruta.save()
        
        # Refrescar el objeto después de la transacción
        ruta.refresh_from_db()
        
        return Response({
            "mensaje": f"{len(paquetes_ids)} paquetes asignados correctamente",
            "total_paquetes": ruta.total_paquetes
        })
       
        
    """Hecho con IA"""
    @action(detail=False, methods=['post'])
    def reasignar_paquete_fallido(self, request):
        """
        Reasigna un paquete fallido a una ruta pendiente.
        URL: POST /api/v1/rutas/reasignar_paquete_fallido/
        Body: {
            "paquete": 69,
            "ruta_destino": 77
        }
        """
        paquete_id = request.data.get('paquete')
        ruta_destino_id = request.data.get('ruta_destino')
        
        if not paquete_id or not ruta_destino_id:
            return Response(
                {"error": "Debes proporcionar 'paquete' y 'ruta_destino'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar paquete
        try:
            paquete = Paquete.objects.select_related('ruta').get(id_paquete=paquete_id)
        except Paquete.DoesNotExist:
            return Response(
                {"error": "Paquete no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if paquete.estado_paquete != "Fallido":
            return Response(
                {"error": "Solo se pueden reasignar paquetes en estado Fallido"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar ruta origen
        ruta_origen = paquete.ruta
        if not ruta_origen or ruta_origen.estado not in ["Completada", "Fallida"]:
            return Response(
                {"error": "El paquete debe pertenecer a una ruta Completada o Fallida"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar ruta destino
        try:
            ruta_destino = Ruta.objects.get(id_ruta=ruta_destino_id)
        except Ruta.DoesNotExist:
            return Response(
                {"error": "Ruta destino no encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if ruta_destino.estado != "Pendiente":
            return Response(
                {"error": "La ruta destino debe estar Pendiente"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reasignar
        with transaction.atomic():
            paquete.ruta = ruta_destino
            paquete.estado_paquete = "Asignado"
            paquete.orden_entrega = None
            paquete.save()
            
            ruta_destino.total_paquetes += 1
            ruta_destino.save()
        
        return Response({
            "mensaje": "Paquete reasignado correctamente",
            "paquete": paquete_id,
            "ruta_origen": ruta_origen.codigo_manifiesto,
            "ruta_destino": ruta_destino.codigo_manifiesto
        })
        
    
    @action(detail=True, methods=['post'])
    def asignar_conductor(self, request, pk=None):
        """
        Asigna un conductor a la ruta.
        Body: {"conductor": 1}
        """
        ruta = self.get_object()
        
        if ruta.estado != "Pendiente":
            return Response(
                {"error": "Solo puedes asignar conductores a rutas Pendientes"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if ruta.total_paquetes == 0:
            return Response(
                {"error": "La ruta debe tener minimo un paquete antes de asignar un conductr"},
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
        if conductor.estado != "Disponible":
            return Response(
                {"error": f"El conductor está {conductor.estado}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que tenga vehículo asignado
        if not conductor.vehiculo:
            return Response(
                {"error": "El conductor no tiene un vehículo asignado"},
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
        
        with transaction.atomic():
            # Asignar conductor
            ruta.conductor = conductor
            ruta.estado = "Asignada"  # CAMBIO AQUÍ
            ruta.save()
            
            # Cambiar estado del conductor a Asignado
            conductor.estado = "Asignado"  # CAMBIO AQUÍ
            conductor.save()
        
        return Response({
            "mensaje": "Conductor asignado correctamente",
            "conductor": conductor.conductor.nombre,
            "ruta": ruta.codigo_manifiesto
        })
        
    
    @action(detail=True, methods=['patch'])
    def reemplazar_conductor(self, request, pk=None):
        """
        Reemplaza el conductor de una ruta Asignada.
        Body: {"conductor": 5}
        """
        ruta = self.get_object()
        
        if ruta.estado != "Asignada":
            return Response(
                {"error": "Solo puedes reemplazar conductores en rutas Asignadas"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        nuevo_conductor_id = request.data.get('conductor')
        
        if not nuevo_conductor_id:
            return Response(
                {"error": "Debes proporcionar el ID del nuevo conductor"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            nuevo_conductor = Driver.objects.get(id_conductor=nuevo_conductor_id)
        except Driver.DoesNotExist:
            return Response(
                {"error": "Conductor no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validaciones del nuevo conductor
        if nuevo_conductor.estado != "Disponible":
            return Response(
                {"error": f"El conductor está {nuevo_conductor.estado}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not nuevo_conductor.vehiculo:
            return Response(
                {"error": "El conductor no tiene un vehículo asignado"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if Ruta.objects.filter(conductor=nuevo_conductor, estado__in=["Asignada", "En ruta"]).exists():
            return Response(
                {"error": "Este conductor ya tiene una ruta activa"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Liberar conductor anterior
            conductor_anterior = ruta.conductor
            if conductor_anterior:
                conductor_anterior.estado = "Disponible"
                conductor_anterior.save()
            
            # Asignar nuevo conductor
            ruta.conductor = nuevo_conductor
            ruta.save()
            
            nuevo_conductor.estado = "Asignado"
            nuevo_conductor.save()
        
        return Response({
            "mensaje": "Conductor reemplazado correctamente",
            "conductor_anterior": conductor_anterior.conductor.nombre if conductor_anterior else "Ninguno",
            "conductor_nuevo": nuevo_conductor.conductor.nombre
        })
        

    @action(detail=False, methods=['get'])
    def ruta_actual(self, request):
        """
        Retorna la ruta asignada a un conductor específico.
        Query Params: driver_id (requerido)
        """
        driver_id = request.query_params.get('driver_id')
        
        if not driver_id:
            return Response(
                {"error": "Se requiere el parámetro driver_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ruta = Ruta.objects.filter(
                conductor_id=driver_id,
                estado__in=["Asignada", "En ruta"]
            ).first()
            
            if not ruta:
                return Response(
                    {"mensaje": "No hay rutas asignadas"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = self.get_serializer(ruta)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    

    @action(detail=True, methods=['post'])
    def calcular_ruta(self, request, pk=None):
        ruta = self.get_object()
        
        # VALIDACIÓN 1: Estado de la ruta
        if ruta.estado not in ["Pendiente", "Asignada"]:
            return Response({
                "error": f"No se puede calcular la ruta en estado '{ruta.estado}'"
            }, status=400)
        
        # VALIDACIÓN 2: Conductor tiene dirección base configurada
        conductor = ruta.conductor
        if not conductor:
            return Response({
                "error": "La ruta no tiene conductor asignado"
            }, status=400)
        
        if not conductor.base_lat or not conductor.base_lng:
            return Response({
                "error": "El conductor no tiene configurada su dirección base",
                "detalle": f"Configure primero la dirección base del conductor {conductor.conductor.nombre}",
                "sugerencia": "Edite el conductor y agregue su dirección base"
            }, status=400)
        
        # VALIDACIÓN 3: Hay paquetes asignados
        if ruta.total_paquetes == 0:
            return Response({"error": "No hay paquetes asignados"}, status=400)

        paquetes = list(ruta.paquetes.all())
        
        # VALIDACIÓN 4: Todos los paquetes tienen coordenadas
        if any(p.lat is None or p.lng is None for p in paquetes):
            return Response({"error": "Hay paquetes sin coordenadas"}, status=400)

        # 1. Punto de partida desde la base del conductor
        start_lat = float(conductor.base_lat)
        start_lng = float(conductor.base_lng)

        # 2. Algoritmo Nearest Neighbor
        restantes = [(float(p.lat), float(p.lng), p) for p in paquetes]
        ordenados = []
        current_lat, current_lng = start_lat, start_lng
        
        while restantes:
            # Calcular distancia REAL con Haversine
            distancias = []
            for lat, lng, paquete in restantes:
                dist = haversine_distance_vectorized(current_lat, current_lng, lat, lng)
                distancias.append((dist, lat, lng, paquete))
            
            # Tomar el más cercano (menor distancia en km)
            _, lat, lng, paquete_cercano = min(distancias, key=lambda x: x[0])
            ordenados.append(paquete_cercano)
            current_lat, current_lng = lat, lng
            restantes = [x for x in restantes if x[2].id_paquete != paquete_cercano.id_paquete]

        # 3. Guardar orden y calcular ruta OSRM
        with transaction.atomic():
            # Guardar orden en paquetes
            for idx, paquete in enumerate(ordenados, 1):
                paquete.orden_entrega = idx
                paquete.save()

            # Construir coordenadas para OSRM
            coordenadas_para_osrm = [
                [start_lng, start_lat]  # Punto inicial del conductor
            ] + [
                [float(p.lng), float(p.lat)] for p in ordenados
            ]
            
            # Convertir a string para OSRM
            coords_str = ";".join([f"{lng},{lat}" for lng, lat in coordenadas_para_osrm])
            
            # 4. Llamar a OSRM
            url = f"https://router.project-osrm.org/route/v1/driving/{coords_str}"
            geometry = None
            distancia_km = None
            duracion_min = None
            
            try:
                resp = requests.get(
                    url, 
                    params={
                        "overview": "full", 
                        "geometries": "geojson",
                        "steps": "false"
                    }, 
                    timeout=10
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("code") == "Ok" and data.get("routes"):
                        route = data["routes"][0]
                        geometry = route["geometry"]
                        distancia_km = round(route["distance"] / 1000, 2)
                        duracion_min = round(route["duration"] / 60)
            except requests.RequestException as e:
                print(f"Error OSRM: {e}")

            # 5. Guardar en la ruta
            ruta.ruta_optimizada = {
                "geometry": geometry,
                "orden_paquetes": [p.id_paquete for p in ordenados],
                "punto_inicio": {"lat": start_lat, "lng": start_lng},
                "paquetes": [
                    {
                        "id": p.id_paquete,
                        "lat": float(p.lat),
                        "lng": float(p.lng),
                        "direccion": p.direccion_entrega,
                        "orden_entrega": idx,
                        "estado": p.estado_paquete  # Para recuperación
                    }
                    for idx, p in enumerate(ordenados, 1)
                ]
            }
            ruta.distancia_total_km = distancia_km
            ruta.tiempo_estimado_minutos = duracion_min
            ruta.save()

        return Response({
            "mensaje": "Ruta optimizada calculada",
            "orden_paquetes": [p.id_paquete for p in ordenados],
            "distancia_km": distancia_km,
            "duracion_min": duracion_min,
            "punto_inicio": {"lat": start_lat, "lng": start_lng}
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
            
            if ruta.conductor and ruta.conductor.vehiculo:
                ruta.vehiculo_usado = ruta.conductor.vehiculo
                
            ruta.save()
            
            # Cambiar estado de paquetes
            ruta.paquetes.update(estado_paquete="En ruta")
            
            # Cambiar estado del conductor
            if ruta.conductor:
                ruta.conductor.estado = "En ruta"
                ruta.conductor.save()
            
            # Cambiar estado del vehículo
            if ruta.conductor.vehiculo:
                ruta.conductor.vehiculo.estado = "En ruta"
                ruta.conductor.vehiculo.save()
        
        return Response({
            "mensaje": "Ruta iniciada correctamente",
            "fecha_inicio": ruta.fecha_inicio,
            "polyline": ruta.ruta_optimizada.get("polyline")
        })
        
        
    @action(detail=True, methods=['get'])
    def proximo_paquete(self, request, pk=None):
        ruta = self.get_object()
        
        proximo = ruta.paquetes.filter(
            estado_paquete__in=['Pendiente', 'Asignado', 'En ruta']
        ).order_by('orden_entrega').first()
        
        if proximo:
            serializer = PaqueteSerializer(proximo)
            return Response({
                'proximo': {
                    **serializer.data,
                    'lat': float(proximo.lat) if proximo.lat else None,
                    'lng': float(proximo.lng) if proximo.lng else None
                },
                'orden': proximo.orden_entrega,
                'total_paquetes': ruta.total_paquetes,
                'entregados': ruta.paquetes_entregados
            })
        
        return Response({
            'proximo': None,
            'mensaje': 'No hay más paquetes pendientes'
        })
        
        
    @action(detail=True, methods=['get'])
    def progreso(self, request, pk=None):
        """
        Devuelve el estado actual de la ruta para persistencia.
        """
        ruta = self.get_object()
        
        paquetes_pendientes = ruta.paquetes.filter(
            estado_paquete__in=['Pendiente', 'Asignado']
        ).order_by('orden_entrega')
        
        paquetes_entregados = ruta.paquetes.filter(
            estado_paquete='Entregado'
        ).order_by('orden_entrega')
        
        paquetes_fallidos = ruta.paquetes.filter(
            estado_paquete='Fallido'
        ).order_by('orden_entrega')
        
        return Response({
            "ruta_id": ruta.id_ruta,
            "estado": ruta.estado,
            "total_paquetes": ruta.total_paquetes,
            "paquetes_entregados": ruta.paquetes_entregados,
            "paquetes_fallidos": ruta.paquetes_fallidos,
            "proximo_paquete": paquetes_pendientes.first().id_paquete if paquetes_pendientes.exists() else None,
            "orden_entrega_actual": paquetes_entregados.count() + paquetes_fallidos.count() + 1,
            "paquetes": {
                "pendientes": [
                    {
                        "id": p.id_paquete,
                        "orden_entrega": p.orden_entrega,
                        "direccion": p.direccion_entrega
                    } for p in paquetes_pendientes
                ],
                "entregados": [
                    {
                        "id": p.id_paquete,
                        "orden_entrega": p.orden_entrega
                    } for p in paquetes_entregados
                ],
                "fallidos": [
                    {
                        "id": p.id_paquete,
                        "orden_entrega": p.orden_entrega
                    } for p in paquetes_fallidos
                ]
            }
        })
        
    
    @action(detail=True, methods=['post'])
    def actualizar_ubicacion(self, request, pk=None):
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
        """
        from django.utils import timezone
        
        ruta = self.get_object()
        
        if ruta.estado != "En ruta":
            return Response(
                {"error": "Solo puedes marcar entregas en rutas activas"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extraer datos
        paquete_id = request.data.get("paquete")
        estado = request.data.get("estado")
        archivo = request.FILES.get("foto")
        
        # Validar que el paquete pertenezca a la ruta
        try:
            paquete = ruta.paquetes.get(id_paquete=paquete_id)
        except Paquete.DoesNotExist:
            return Response(
                {"error": "El paquete no pertenece a esta ruta"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que el paquete esté en ruta
        if paquete.estado_paquete != "En ruta":
            return Response({"error": "El paquete debe estar En ruta para marcar entrega"}, 400)
        
        with transaction.atomic():
            # 1. Crear registro de entrega
            data = {
                "paquete": paquete_id,
                "ruta": ruta.id_ruta,
                "estado": estado,
                "observacion": request.data.get("observacion", ""),
                "lat_entrega": request.data.get("lat_entrega", paquete.lat),
                "lng_entrega": request.data.get("lng_entrega", paquete.lng),
                "foto": archivo
            }
            
            serializer = EntregaPaqueteSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            entrega = serializer.save()
            
            # Procesar imagen si existe
            if archivo:
                self.handle_imagen(entrega, archivo)
            
            # 2. Actualizar estado del paquete original
            if estado == "Entregado":
                paquete.estado_paquete = "Entregado"
                ruta.paquetes_entregados += 1
            else:  # Fallido
                paquete.estado_paquete = "Fallido"
                ruta.paquetes_fallidos += 1
            
            paquete.fecha_entrega = timezone.now()
            paquete.save()
            
            # 3. Actualizar conductor si está en la ruta
            if ruta.conductor:
                conductor = ruta.conductor
                conductor.ubicacion_actual_lat = data['lat_entrega']
                conductor.ubicacion_actual_lng = data['lng_entrega']
                conductor.ultima_actualizacion_ubicacion = timezone.now()
                conductor.save()
            
            # 4. Verificar si la ruta está completa
            # entregados_total = ruta.paquetes_entregados + ruta.paquetes_fallidos
            # if entregados_total >= ruta.total_paquetes:
            #     ruta.estado = Ruta.EstadoRuta.COMPLETADA
            #     ruta.fecha_fin = timezone.now()
            #     
            #     # Liberar conductor
            #     if ruta.conductor:
            #         ruta.conductor.estado = Driver.status_driver.DISPONIBLE
            #         ruta.conductor.save()
            
            # ruta.save()
        
        # 5. Buscar próximo paquete
        proximo = ruta.paquetes.filter(
            estado_paquete__in=['Pendiente', 'Asignado']
        ).order_by('orden_entrega').first()
        
        respuesta = {
            "mensaje": "Entrega registrada correctamente",
            "imagen": entrega.imagen,
            "progreso": {
                "entregados": ruta.paquetes_entregados,
                "fallidos": ruta.paquetes_fallidos,
                "total": ruta.total_paquetes,
                "porcentaje": round((ruta.paquetes_entregados + ruta.paquetes_fallidos) / ruta.total_paquetes * 100, 2)
            },
            "ruta_estado": ruta.estado
        }
        
        # Si hay próximo paquete, incluirlo en la respuesta
        if proximo:
            respuesta["proximo_paquete"] = {
                "id": proximo.id_paquete,
                "orden_entrega": proximo.orden_entrega,
                "direccion": proximo.direccion_entrega
            }
        
        return Response(respuesta)
    
    
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

            if ruta.paquetes_fallidos > ruta.paquetes_entregados:
                ruta.estado = "Fallida"
            else:
                ruta.estado = "Completada"
            
            ruta.fecha_fin = timezone.now()
            ruta.save()
                    
            
            # Liberar conductor
            if ruta.conductor:
                # Lo guardo primero para luego declarar la fk como None
                vehiculo = ruta.conductor.vehiculo
                
                ruta.conductor.estado = "Disponible"
                ruta.conductor.vehiculo = None
                ruta.conductor.save()
            
            
            if vehiculo:
                vehiculo.estado = "Disponible"
                vehiculo.save()
        
        return Response({
            "mensaje": f"Ruta cerrada con estado: {ruta.estado}",
            "entregados": ruta.paquetes_entregados,
            "fallidos": ruta.paquetes_fallidos
        })
        
    
    @action(detail=False, methods=['get']) 
    def historial_conductor(self, request):
        """
        Retorna el historial de rutas Completadas -Fallidas de un conductor específico.
        Query Params: driver_id
        """
        driver_id = request.query_params.get('driver_id')
        
        if not driver_id:
            return Response(
                {"error": "Debe proporcionar el id del conductor"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verificar que el conductor exista
            conductor = Driver.objects.get(id_conductor=driver_id)
            
            # Filtrar rutas completadas o fallidas del conductor
            rutas = Ruta.objects.filter(
                conductor=conductor,
                estado__in=["Completada", "Fallida"]
            ).select_related('conductor').prefetch_related('paquetes').order_by('-fecha_fin')
            
            serializer = self.get_serializer(rutas, many=True)
            return Response(serializer.data)
            
        except Driver.DoesNotExist:
            return Response(
                {"error": "Conductor no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            


    @action(detail=True, methods=['get'])
    def exportar_pdf(self, request, pk=None):
        ruta = self.get_object()

        if ruta.estado not in ["Completada", "Fallida"]:
            return Response(
                {"error": "Solo puedes exportar rutas completadas o fallidas"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generar PDF en memoria
        buffer = generar_pdf_ruta(ruta, logo_path="static/images/logo.png")
        pdf_bytes = buffer.getvalue()

        # Enviar el PDF directo al frontend
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=ruta_{ruta.codigo_manifiesto}.pdf'

        return response
