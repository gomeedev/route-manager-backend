from django.urls import path
from .views import NovedadListCreateView, NovedadDetailsView


urlpatterns = [
    path("", NovedadListCreateView.as_view(), name="novedad-list-create"),
    path("<int:pk>/", NovedadDetailsView.as_view(), name="novedades-detail")
]
