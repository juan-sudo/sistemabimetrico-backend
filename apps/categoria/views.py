from apps.categoria.models import Categoria
from apps.categoria.serializers import CategoriaSerializer
from apps.core.api import BaseModelViewSet


class CategoriaViewSet(BaseModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
