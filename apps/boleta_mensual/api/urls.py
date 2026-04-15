from rest_framework.routers import DefaultRouter

from .views import BoletaMensualViewSet


router = DefaultRouter()
router.register("boletas-mensuales", BoletaMensualViewSet, basename="boletas-mensuales")

urlpatterns = router.urls
