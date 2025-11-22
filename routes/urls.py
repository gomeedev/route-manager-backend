from rest_framework.routers import DefaultRouter
from .views import RutaViewSet

router = DefaultRouter()
router.register(r"", RutaViewSet, basename="rutas")

urlpatterns = router.urls
