from django.db.models import Q, Sum
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Livro
from core.models.compra import Compra
from core.serializers import (
    LivroAjustarEstoqueSerializer,
    LivroAlterarPrecoSerializer,
    LivroListSerializer,
    LivroMaisVendidoSerializer,
    LivroRetrieveSerializer,
    LivroSerializer,
)


class LivroViewSet(ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return LivroListSerializer
        elif self.action == 'retrieve':
            return LivroRetrieveSerializer
        return LivroSerializer

    @action(detail=True, methods=['patch'])
    def alterar_preco(self, request, pk=None):
        livro = self.get_object()

        serializer = LivroAlterarPrecoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        livro.preco = serializer.validated_data['preco']
        livro.save()

        return Response(
            {'detail': f'Preço do livro "{livro.titulo}" atualizado para {livro.preco}.'}, status=status.HTTP_200_OK
        )

    @extend_schema(
        summary='Lista os livros mais vendidos',
        description='Retorna os livros que venderam mais de 10 unidades.',
        responses={200: LivroMaisVendidoSerializer(many=True)},
    )
    @action(detail=False, methods=['get'])
    def mais_vendidos(self, request):
        quantidade_minima_vendidos = 100
        livros = (
            Livro.objects
            .annotate(
                total_vendidos=Sum(
                    'itens_compra__quantidade', filter=Q(itens_compra__compra__status=Compra.StatusCompra.FINALIZADO)
                )
            )
            .filter(total_vendidos__gt=quantidade_minima_vendidos)
            .order_by('-total_vendidos')
        )

        serializer = LivroMaisVendidoSerializer(livros, many=True)

        if not serializer.data:
            return Response(
                {'detail': f"Nenhum livro excedeu {quantidade_minima_vendidos} vendas."}, status=status.HTTP_200_OK
            )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Ajusta o estoque de um livro",
        description="Aumenta ou diminui o estoque; impede resultado negativo.",
        request=LivroAjustarEstoqueSerializer,
        responses={
            200: OpenApiResponse(
                response=None,
                description="Estoque ajustado com sucesso.",
                examples=[
                    {
                        "status": "Quantidade ajustada com sucesso",
                        "novo_estoque": 30
                    }
                ]
            ),
            400: OpenApiResponse(
                description="Erro de validação",
                examples=[
                    {"quantidade": "A quantidade em estoque não pode ser negativa."}
                ]
            ),
        },
        )
    @action(detail=True, methods=['post'])
    def ajustar_estoque(self, request, pk=None):
        livro = self.get_object()

        serializer = LivroAjustarEstoqueSerializer(data=request.data, context={'livro': livro})
        serializer.is_valid(raise_exception=True)

        quantidade_ajuste = serializer.validated_data['quantidade']
        livro.quantidade += quantidade_ajuste
        livro.save()

        return Response(
            {'status': 'Quantidade ajustada com sucesso', 'novo_estoque': livro.quantidade},
            status=status.HTTP_200_OK
        )
