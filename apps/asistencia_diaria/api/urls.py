from rest_framework.routers import DefaultRouter

from .views import AsistenciaDiariaViewSet


router = DefaultRouter()
router.register("asistencias-diarias", AsistenciaDiariaViewSet, basename="asistencias-diarias")

urlpatterns = router.urls
