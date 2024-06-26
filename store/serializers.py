from django.db import transaction
from rest_framework import serializers
from .models import Collection, Product, Promotion, Customer, Review, Cart, CartItem, Order, OrderItem, ProductImage
from .signals import order_created
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


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)


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
        user_id = self.context['user_id']
        return Review.objects.create(product_id=product_id, user_id=user_id, **validated_data)


class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'title', 'content']


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    # catching errors if product is not found
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value):
            raise serializers.ValidationError('Product not found')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            # Updating:
            # increase quantity when adding same product
            cart_item = CartItem.objects.get(
                cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            # Creating
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


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


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'payment_status', 'items', 'placed_at']


class OrderCreationSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        # validate if cart exists
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError(
                'No cart with the given ID was found.')
        # validate if cart is not empty
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty.')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            customer = Customer.objects.get(user_id=self.context['user_id'])

            order = Order.objects.create(customer_id=customer.id)

            cart_items = CartItem.objects.select_related(
                'product').filter(cart_id=cart_id)

            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                ) for item in cart_items
            ]

            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()

            order_created.send_robust(self.__class__, order=order)

            return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']
