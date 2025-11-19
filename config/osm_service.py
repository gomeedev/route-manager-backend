import requests
from decimal import Decimal
import time


class OSMService:
    
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    
    @staticmethod
    def geocodificar_direccion(direccion_completa):
        """
        Geocodifica una dirección a coordenadas lat/lng usando OSM
        
        Args:
            direccion_completa (str): Dirección completa con ciudad y país
            
        Returns:
            dict: {'lat': Decimal, 'lng': Decimal} o None si falla
        """
        try:
            params = {
                'q': direccion_completa,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'co',  # Limitar a Colombia
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'RouteManager/1.0'  # Nominatim requiere identificarte
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
            # Respetar límite de 1 request/segundo de Nominatim
            time.sleep(1)