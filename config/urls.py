from django.contrib import admin
from django.urls import path, include
# Mòdulo de documentaciòn
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView



urlpatterns = [
    
    # Endpoints de empresa
    path("api/v1/", include('empresa.urls')),
    
    # Endpoints de ['rol', 'usuario']
    path("api/v1/", include('users.urls')),
    
    # Endpoints de driver
    path("api/v1/drivers/", include("drivers.urls")),
    
    # Endpoints de novedades
    path("api/v1/novedades/", include("novedades.urls")),
    
    # Endpoints vehiculos
    path("api/v1/vehiculos/", include("vehicles.urls")),
    
    # Mòdulo del admin
    path('admin/', admin.site.urls),
    
    # Endpoints sobre la documentación
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"), 
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
