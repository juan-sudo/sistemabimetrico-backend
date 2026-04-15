from rest_framework.routers import DefaultRouter

from apps.justificacion.views import JustificacionViewSet


router = DefaultRouter()
router.register("justificaciones", JustificacionViewSet, basename="justificaciones")

urlpatterns = router.urls
