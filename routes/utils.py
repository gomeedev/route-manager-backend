import numpy as np
from math import radians, sin, cos, sqrt, atan2




def haversine_distance_vectorized(lat1, lng1, lat2_array, lng2_array):
    """
    Versión vectorizada para calcular múltiples distancias a la vez.
    Más eficiente cuando hay muchos paquetes.
    """
    R = 6371
    
    lat1, lng1 = radians(lat1), radians(lng1)
    lat2 = np.radians(lat2_array)
    lng2 = np.radians(lng2_array)
    
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlng/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    
    return R * c

def nearest_neighbor_haversine(start_lat, start_lng, paquetes):
    """
    Algoritmo Nearest Neighbor optimizado con cálculo vectorizado.
    paquetes: lista de diccionarios con 'lat', 'lng', 'id'
    """
    if not paquetes:
        return []
    
    import numpy as np
    paquetes = paquetes.copy()
    ordenados = []
    current_lat, current_lng = start_lat, start_lng
    
    # Convertir a arrays para vectorización
    lats = np.array([p['lat'] for p in paquetes])
    lngs = np.array([p['lng'] for p in paquetes])
    ids = [p['id'] for p in paquetes]
    
    while len(paquetes) > 0:
        # Calcular distancias a todos los paquetes restantes
        distancias = haversine_distance_vectorized(current_lat, current_lng, lats, lngs)
        
        # Encontrar índice del más cercano
        idx_min = np.argmin(distancias)
        
        # Agregar a ordenados
        ordenados.append(paquetes[idx_min])
        
        # Actualizar posición actual
        current_lat, current_lng = paquetes[idx_min]['lat'], paquetes[idx_min]['lng']
        
        # Remover el seleccionado
        paquetes.pop(idx_min)
        lats = np.delete(lats, idx_min)
        lngs = np.delete(lngs, idx_min)
    
    return ordenados
