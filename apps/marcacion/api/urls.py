from rest_framework.routers import DefaultRouter

from apps.marcacion.views import MarcacionViewSet


router = DefaultRouter()
router.register("marcaciones", MarcacionViewSet, basename="marcaciones")

urlpatterns = router.urls
