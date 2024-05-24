from rest_framework import serializers
from .models import Collection, Product, Promotion, Customer, Review, Cart, CartItem
from decimal import Decimal


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'name', 'products_count']


class ProductReadSerializer(serializers.ModelSerializer):
    collection = CollectionSerializer()

    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')

    price = serializers.SerializerMethodField(
        method_name='convert_price')

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price',
                  'price_with_tax', 'quantity', 'promotion', 'collection']

    def calculate_tax(self, product):
        return product.unit_price * Decimal(1.5)

    def convert_price(self, product):
        return int(product.unit_price)


class ProductWriteSerializer(serializers.ModelSerializer):
    promotion = serializers.PrimaryKeyRelatedField(
        queryset=Promotion.objects.all(), many=True, required=False, allow_null=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'description',
                  'unit_price', 'quantity', 'promotion', 'collection']


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'unit_price']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'phone', 'birthdate', 'membership']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'title', 'content', 'created_at', 'user_id']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'created_at', 'total_price']
