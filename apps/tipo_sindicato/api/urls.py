from rest_framework.routers import DefaultRouter

from .views import TipoSindicatoViewSet


router = DefaultRouter()
router.register("tipos-sindicato", TipoSindicatoViewSet, basename="tipos-sindicato")

urlpatterns = router.urls
