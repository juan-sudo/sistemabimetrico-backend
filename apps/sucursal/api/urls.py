from rest_framework.routers import DefaultRouter

from .views import SucursalViewSet


router = DefaultRouter()
router.register("sucursales", SucursalViewSet, basename="sucursales")

urlpatterns = router.urls
