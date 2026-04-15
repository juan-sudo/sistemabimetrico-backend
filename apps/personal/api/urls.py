from rest_framework.routers import DefaultRouter

from .views import PersonalViewSet, UbicacionGeograficaViewSet


router = DefaultRouter()
router.register("ubicaciones-geograficas", UbicacionGeograficaViewSet, basename="ubicaciones-geograficas")
router.register("personales", PersonalViewSet, basename="personales")

urlpatterns = router.urls
