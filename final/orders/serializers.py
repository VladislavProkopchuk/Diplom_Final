"""
Классы сериализации
"""
from rest_framework import serializers

from .models import CustomUser, Product, ProductInfo, Order, OrderItem, Contact


# pylint: disable = too-few-public-methods, missing-class-docstring

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "type",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """
        Создание пользователя
        """
        user = CustomUser.objects.create_user(**validated_data)
        return user


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "category")


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = ProductInfo
        fields = ("id", "product", "shop", "quantity", "price", "price_rrc", "name")


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = (
            "id",
            "user",
            "type",
            "value",
            "city",
            "street",
            "house",
            "structure",
            "building",
            "apartment",
            "phone",
        )


class OrderItemSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer()

    class Meta:
        model = OrderItem
        fields = ("id", "order", "product_info", "quantity", "product_info")


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ("id", "user", "dt", "status", "contact", "ordered_items")
