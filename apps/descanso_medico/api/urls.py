from rest_framework.routers import DefaultRouter

from .views import DescansoMedicoViewSet


router = DefaultRouter()
router.register("descansos-medicos", DescansoMedicoViewSet, basename="descansos-medicos")

urlpatterns = router.urls
