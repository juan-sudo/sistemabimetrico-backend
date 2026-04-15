from rest_framework.routers import DefaultRouter

from .views import DescargaMarcacionViewSet


router = DefaultRouter()
router.register("descargas-marcaciones", DescargaMarcacionViewSet, basename="descargas-marcaciones")

urlpatterns = router.urls
