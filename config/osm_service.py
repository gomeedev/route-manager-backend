# config/osm_service.py
import requests
from decimal import Decimal
import time


""" Hecho con IA """
class OSMService:
    
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    OSRM_URL = "https://router.project-osrm.org/route/v1/driving"
    
    @staticmethod
    def geocodificar_direccion(direccion_completa):
        """
        Geocodifica una dirección a coordenadas lat/lng usando OSM
        """
        try:
            params = {
                'q': direccion_completa,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'co',
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'RouteManager/1.0'
            }
            
            response = requests.get(
                OSMService.NOMINATIM_URL, 
                params=params, 
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                return {
                    'lat': Decimal(str(result['lat'])),
                    'lng': Decimal(str(result['lon']))
                }
            
            return None
            
        except requests.RequestException as e:
            print(f"Error en geocodificación OSM: {e}")
            return None
        
        finally:
            time.sleep(1)
    
    
    @staticmethod
    def calcular_ruta_optimizada(coordenadas):
        """
        Calcula la ruta optimizada usando OSRM.
        
        Args:
            coordenadas: Lista de tuplas [(lat1, lng1), (lat2, lng2), ...]
            
        Returns:
            dict: {
                'polyline': str,
                'distancia_km': float,
                'duracion_minutos': int,
                'orden': [0, 1, 2, ...]  # Índices en el orden original
            }
            o None si falla
        """
        if len(coordenadas) < 2:
            return None
        
        try:
            # Formato OSRM: lng,lat;lng,lat;lng,lat
            coords_str = ";".join([f"{lng},{lat}" for lat, lng in coordenadas])
            
            url = f"{OSMService.OSRM_URL}/{coords_str}"
            
            params = {
                'overview': 'full',
                'geometries': 'geojson',
                'steps': 'false'
            }
            
            headers = {
                'User-Agent': 'RouteManager/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') != 'Ok':
                print(f"Error OSRM: {data.get('message')}")
                return None
            
            route = data['routes'][0]
            
            # Extraer geometría (polyline en formato GeoJSON)
            geometry = route['geometry']
            
            # Convertir a string para guardar en JSON
            polyline = str(geometry['coordinates'])
            
            # Distancia en metros → km
            distancia_km = round(route['distance'] / 1000, 2)
            
            # Duración en segundos → minutos
            duracion_minutos = round(route['duration'] / 60)
            
            # OSRM no reordena automáticamente, mantiene el orden dado
            orden = list(range(len(coordenadas)))
            
            return {
                'polyline': polyline,
                'geometry': geometry,  # GeoJSON completo para el frontend
                'distancia_km': distancia_km,
                'duracion_minutos': duracion_minutos,
                'orden': orden
            }
            
        except requests.RequestException as e:
            print(f"Error en OSRM: {e}")
            return None
        
        finally:
            time.sleep(0.5)  # Rate limit más flexible que Nominatim