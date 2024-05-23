from django.db.models.aggregates import Count
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Collection, Product
from .pagination import CustomPagination
from .filters import ProductFilter
from . import serializers


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
        products_count=Count('product')
    )
    serializer_class = serializers.CollectionSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related(
        'collection').prefetch_related('promotion')
    serializer_class = serializers.ProductSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    pagination_class = CustomPagination
    ordering_fields = ['id', 'title', 'unit_price',
                       'quantity']
    filterset_class = ProductFilter
