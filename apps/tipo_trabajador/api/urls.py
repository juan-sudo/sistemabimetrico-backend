from rest_framework.routers import DefaultRouter

from .views import TipoTrabajadorViewSet


router = DefaultRouter()
router.register("tipos-trabajador", TipoTrabajadorViewSet, basename="tipos-trabajador")

urlpatterns = router.urls
