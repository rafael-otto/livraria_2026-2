from rest_framework.viewsets import ModelViewSet

from core.models import Compra
from core.serializers import CompraSerializer


class CompraViewSet(ModelViewSet):
    queryset = Compra.objects.order_by("-id")
    serializer_class = CompraSerializer
