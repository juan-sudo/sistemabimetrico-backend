from rest_framework.routers import DefaultRouter

from apps.dispositivo.views import DispositivoViewSet


router = DefaultRouter()
router.register("dispositivos", DispositivoViewSet, basename="dispositivos")

urlpatterns = router.urls
