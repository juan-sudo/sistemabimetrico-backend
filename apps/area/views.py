from apps.area.models import Area
from apps.area.serializers import AreaSerializer
from apps.core.api import BaseModelViewSet


class AreaViewSet(BaseModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
