from rest_framework import serializers

from .models import Product, ProductInfo, Shop, Category, Order, OrderItem
from order_service.users.serializers import ContactSerializer


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ["id", "name", "url", "user", "is_accepting_orders"]
        read_only_fields = ["id", "name", "url", "user"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ["id", "name", "category"]


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    shop = ShopSerializer()

    class Meta:
        model = ProductInfo
        fields = [
            "id",
            "model",
            "external_id",
            "product",
            "shop",
            "quantity",
            "price",
            "price_rrc",
        ]


class BasketAddItemSerializer(serializers.Serializer):
    product_info = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class BasketAddSerializer(serializers.Serializer):
    items = BasketAddItemSerializer(many=True)


class BasketUpdateItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class BasketUpdateSerializer(serializers.Serializer):
    items = BasketUpdateItemSerializer(many=True)


class BasketDeleteSerializer(serializers.Serializer):
    items = serializers.ListField(child=serializers.IntegerField(min_value=1))


class OrderItemSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer()
    total = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_info",
            "quantity",
            "total",
        ]


class OrderSerializer(serializers.ModelSerializer):
    total = serializers.IntegerField(read_only=True)
    ordered_items = OrderItemSerializer(many=True, read_only=True)
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "created_at",
            "state",
            "contact",
            "total",
            "ordered_items",
        ]
        read_only_fields = ["id", "created_at", "state", "total"]


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["contact"]
