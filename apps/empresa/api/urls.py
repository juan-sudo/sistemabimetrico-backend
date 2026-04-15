from rest_framework.routers import DefaultRouter

from .views import EmpresaViewSet


router = DefaultRouter()
router.register("empresas", EmpresaViewSet, basename="empresas")

urlpatterns = router.urls
