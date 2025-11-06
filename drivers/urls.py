from django.urls import path
from .views import DriverListView, DriverDetailView, DriverStateUpdateView


urlpatterns = [
    path("", DriverListView.as_view(), name="drivers-list"),
    path("<int:id_conductor>/", DriverDetailView.as_view(), name="drivers-datails"),
    path("<int:id_conductor>/estado/", DriverStateUpdateView.as_view(), name="drivers-update-estado"),
    
]