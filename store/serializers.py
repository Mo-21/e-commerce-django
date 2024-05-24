from rest_framework import serializers
from .models import Collection, Product, Promotion, Customer, Review
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
