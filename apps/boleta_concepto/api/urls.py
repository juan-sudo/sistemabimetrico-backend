from rest_framework.routers import DefaultRouter

from .views import BoletaConceptoViewSet


router = DefaultRouter()
router.register("boletas-conceptos", BoletaConceptoViewSet, basename="boletas-conceptos")

urlpatterns = router.urls
