from django.db.models.aggregates import Count
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Collection, Product, Customer
from .pagination import CustomPagination
from .filters import ProductFilter
from .permissions import IsAdminOrReadOnly
from . import serializers


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
        products_count=Count('product')
    )
    serializer_class = serializers.CollectionSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['id', 'products_count']
    permission_classes = [IsAdminOrReadOnly]


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related(
        'collection').prefetch_related('promotion')
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    pagination_class = CustomPagination
    ordering_fields = ['id', 'title', 'unit_price',
                       'quantity']
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = ProductFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ProductReadSerializer
        return serializers.ProductWriteSerializer


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.select_related('user').all()
    serializer_class = serializers.CustomerSerializer
    pagination_class = CustomPagination
