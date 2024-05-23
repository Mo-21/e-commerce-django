from django.db.models.aggregates import Count
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
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
    queryset = Customer.objects.all()
    serializer_class = serializers.CustomerSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['GET', 'PATCH'], permission_classes=[IsAuthenticated])
    def me(self, request):
        (customer, is_created) = Customer.objects.get_or_create(
            user_id=request.user.id)
        if request.method == 'GET':
            serializer = serializers.CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'Patch':
            serializer = serializers.CustomerSerializer(
                customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
