from rest_framework import serializers

from .models import Contact, User


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "id",
            "user",
            "city",
            "street",
            "house",
            "structure",
            "building",
            "apartment",
            "phone",
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "company",
            "position",
        ]
        read_only_fields = ["id", "email"]
