from django.urls import path
from .views import DriverListView, DriverStateUpdateView


urlpatterns = [
    path("", DriverListView.as_view(), name="drivers-list"),
    path("<int:conductor_id>/", DriverStateUpdateView.as_view(), name="drivers-update")
]