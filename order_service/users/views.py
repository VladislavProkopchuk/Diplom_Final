from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from order_service.shops.permissions import IsBuyer

from .serializers import ContactSerializer, UserSerializer


@extend_schema_view(
    get=extend_schema(description="Получение контактов покупателя"),
    post=extend_schema(description="Создание контакта покупателя"),
)
class ContactList(generics.ListCreateAPIView):
    permission_classes = [IsBuyer]
    serializer_class = ContactSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return user.contacts.all()


@extend_schema_view(
    get=extend_schema(description="Получение контакта покупателя"),
    put=extend_schema(description="Изменение контакта покупателя"),
    patch=extend_schema(description="Изменение контакта покупателя"),
    delete=extend_schema(description="Удаление контакта покупателя"),
)
class ContactDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsBuyer]
    serializer_class = ContactSerializer

    def get_queryset(self):
        user = self.request.user
        return user.contacts.all()


class UserDetail(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        """Получение информации о пользователе"""
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def post(self, request):
        """Изменение информации о пользователе"""
        user = request.user
        serializer = UserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
