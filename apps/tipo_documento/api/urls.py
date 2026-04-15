from rest_framework.routers import DefaultRouter

from .views import TipoDocumentoViewSet


router = DefaultRouter()
router.register("tipos-documento", TipoDocumentoViewSet, basename="tipos-documento")

urlpatterns = router.urls
