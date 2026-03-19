from rest_framework.viewsets import ModelViewSet

from core.models import Categoria
from core.serializers import CategoriaSerializer


class CategoriaViewSet(ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

#   queryset = Categoria.objects.order_by("descricao") para organizar em ordem alfabética
#   se eu quiser inverter é só colocar um "-", ex .all("-id")
