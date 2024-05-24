from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Collection, Product, Customer, Review
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
        elif request.method == 'PATCH':
            serializer = serializers.CustomerSerializer(
                customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class ReviewViewSet(ModelViewSet):
    # TODO: allow put only if the review is created by the current user
    serializer_class = serializers.ReviewSerializer
    pagination_class = CustomPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at']
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_id = self.kwargs['product_pk']
        get_object_or_404(Product, id=product_id)
        return Review.objects.filter(product_id=product_id)

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
