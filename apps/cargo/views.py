from apps.cargo.models import Cargo
from apps.cargo.serializers import CargoSerializer
from apps.core.api import BaseModelViewSet


class CargoViewSet(BaseModelViewSet):
    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer
