from rest_framework import serializers
from .models import Collection, Product
from decimal import Decimal


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'name', 'products_count']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price',
                  'price_with_tax', 'quantity', 'promotion', 'collection']

    collection = CollectionSerializer()

    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')

    price = serializers.SerializerMethodField(
        method_name='convert_price')

    def calculate_tax(self, product):
        return product.unit_price * Decimal(1.5)

    def convert_price(self, product):
        return int(product.unit_price)
