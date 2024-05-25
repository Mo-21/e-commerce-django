from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.serializers import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from .models import Collection, Product, Customer, Review, Cart, CartItem, Order, OrderItem
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
    pagination_class = CustomPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at']
    permission_classes = [IsAuthenticatedOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        product_id = self.kwargs['product_pk']
        get_object_or_404(Product, id=product_id)
        return Review.objects.filter(product_id=product_id)

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return serializers.ReviewUpdateSerializer
        return serializers.ReviewSerializer

    def get_serializer_context(self):
        return {
            'product_id': self.kwargs['product_pk'],
            'user_id': self.request.user.id
        }

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Check if the current user is the author of the review
        if request.user.id != instance.user.id:
            return Response(
                {'details': 'You do not have permission to edit this review.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = serializers.ReviewUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return serializers.UpdateCartItemSerializer
        return serializers.CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = serializers.CartSerializer


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = serializers.OrderCreationSerializer(
            data=request.data,
            context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = serializers.OrderSerializer(order)
        return Response(serializer.data)

    def get_queryset(self):
        current_user = self.request.user
        order_customer_id = Customer.objects.only(
            'id').get(user_id=current_user.id)

        if current_user.is_staff:
            return Order.objects.prefetch_related('items__product').all()
        elif current_user.id == order_customer_id:
            return Order.objects.prefetch_related('items__product').filter(customer_id=order_customer_id)
        return Order.objects.prefetch_related('items__product').all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.OrderCreationSerializer
        return serializers.OrderSerializer
