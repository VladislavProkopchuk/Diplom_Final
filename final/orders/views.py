"""
Представления для REST
"""
import requests
import yaml

from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import URLValidator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import (
    Category,
    Contact,
    Order,
    OrderItem,
    Parameter,
    Product,
    ProductInfo,
    ProductParameter,
    Shop,
)
from .serializers import (
    ContactSerializer,
    OrderSerializer,
    ProductInfoSerializer,
    UserSerializer, OrderItemSerializer,
)

from django.conf import settings


class RegisterView(APIView):
    """
    Регистрирует нового пользователя и отправляет ему приветственное письмо.

    Параметры:
    - username (str): имя пользователя
    - email (str): электронная почта пользователя
    - first_name (str): имя пользователя
    - last_name (str): фамилия пользователя
    - password (str): пароль пользователя

    Возвращает:
    - status (str): статус создания пользователя
    - email_status (str): статус отправки email
    """
    @extend_schema(
        summary='Регистрация нового пользователя',
        description='Регистрирует нового пользователя и отправляет приветственное письмо, если возможно.',
        request=UserSerializer,
        responses={201: OpenApiResponse(description='Пользователь успешно создан', response=UserSerializer)},
        parameters=[
            OpenApiParameter(name='username', description='Имя пользователя', required=True, type=OpenApiTypes.STR),
            OpenApiParameter(name='email', description='Электронная почта пользователя', required=True, type=OpenApiTypes.STR),
            OpenApiParameter(name='first_name', description='Имя', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='last_name', description='Фамилия', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='password', description='Пароль', required=True, type=OpenApiTypes.STR),
        ]
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Попытка отправки email
            try:
                send_mail(
                    'Welcome to our service',
                    'Thank you for registering.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                email_status = "Email sent successfully"
            except Exception as e:
                email_status = f"Registration successful, but failed to send email: {str(e)}"

            return Response({"status": "User created successfully", "email_status": email_status},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Авторизация пользователя и выдача токена для доступа к API.

    Параметры:
    - email (str): электронная почта пользователя
    - password (str): пароль пользователя

    Возвращает:
    - status (str): статус авторизации
    - token (str): токен доступа, если авторизация успешна
    """
    @extend_schema(
        parameters=[
            OpenApiParameter(name='email', description='Email пользователя', required=True, type=OpenApiTypes.STR),
            OpenApiParameter(name='password', description='Пароль пользователя', required=True, type=OpenApiTypes.STR)
        ],
        responses={200: OpenApiResponse(description='Успешный вход в систему')}
    )
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {"status": "Login successful", "token": token.key},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


class ProductInfoViewSet(ModelViewSet):
    """
    Предоставляет CRUD операции для информации о продуктах.

    Фильтры:
    - category (str): фильтрация по категории продукта

    Возвращает:
    - список информации о продуктах
    """
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer

    @extend_schema(
        summary='Получение и управление информацией о продуктах',
        description='Позволяет получать, создавать, редактировать и удалять информацию о продуктах.',
        parameters=[
            OpenApiParameter(name='category', description='Фильтр по имени категории продукта', required=False, type=OpenApiTypes.STR)
        ]
    )
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(product__category__name=category)
        return queryset


class CartView(APIView):
    """
    Управление корзиной пользователя: добавление, просмотр, удаление товаров.

    GET:
    Возвращает текущее состояние корзины пользователя.

    POST:
    Добавляет товар в корзину.
    - product_info_id (int): идентификатор информации о продукте
    - quantity (int): количество товара для добавления

    DELETE:
    Удаляет товар из корзины.
    - product_info_id (int): идентификатор информации о продукте
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Просмотр и управление корзиной',
        description='Позволяет просматривать, добавлять или удалять товары в корзине пользователя.',
        responses={
            200: OpenApiResponse(description='Корзина получена или обновлена успешно', response=OrderSerializer),
            404: OpenApiResponse(description='Корзина не найдена')
        }
    )
    def get(self, request):
        order = get_object_or_404(Order, user=request.user, status="basket")
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @extend_schema(
        request=OrderItemSerializer,
        responses={200: OpenApiResponse(description='Товар добавлен в корзину')}
    )
    def post(self, request):
        order, created = Order.objects.get_or_create(user=request.user, status="basket")
        product_info_id = request.data.get("product_info_id")
        quantity = request.data.get("quantity")
        product_info = get_object_or_404(ProductInfo, id=product_info_id)
        order_item, created = OrderItem.objects.get_or_create(
            order=order, product_info=product_info, defaults={"quantity": quantity}
        )
        if not created:
            order_item.quantity += int(quantity)
            order_item.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @extend_schema(
        request=None,  # Удаление не требует тела запроса
        responses={200: OpenApiResponse(description='Товар удален из корзины')}
    )
    def delete(self, request):
        order = get_object_or_404(Order, user=request.user, status="basket")
        product_info_id = request.data.get("product_info_id")
        product_info = get_object_or_404(ProductInfo, id=product_info_id)
        order_item = get_object_or_404(
            OrderItem, order=order, product_info=product_info
        )
        order_item.delete()
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class ContactViewSet(ModelViewSet):
    """
    Управление контактами пользователя: создание, просмотр, обновление, удаление.

    Возвращает список контактов пользователя или детали конкретного контакта.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ContactSerializer

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)


class ConfirmOrderView(APIView):
    """
    Подтверждение заказа пользователя и отправка уведомления на email.

    Параметры:
    - contact_id (int): идентификатор контакта для доставки заказа

    Возвращает:
    - status (str): статус подтверждения заказа
    - email_status (str): статус отправки уведомления на email
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        contact_id = request.data.get("contact_id")

        try:
            contact = Contact.objects.get(id=contact_id, user=user)
            order = Order.objects.get(user=user, status="basket")
            order.contact = contact
            order.status = "confirmed"
            order.save()

            # Попытка отправки email
            try:
                send_mail(
                    'Order Confirmation',
                    f'Your order #{order.id} has been confirmed.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                email_status = "Email sent successfully"
            except Exception as e:
                email_status = f"Order confirmed, but failed to send email: {str(e)}"

            return Response({"status": "Order confirmed", "email_status": email_status}, status=status.HTTP_200_OK)

        except Contact.DoesNotExist:
            return Response({"error": "Contact not found"}, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            return Response({"error": "Basket not found"}, status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(ModelViewSet):
    """
    Управление заказами пользователя: просмотр списка заказов и деталей конкретного заказа.

    Исключает заказы со статусом "basket" (корзина).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).exclude(status="basket")


class ImportProducts(APIView):
    """
    Импорт товаров от поставщика через URL или файл.

    Параметры:
    - url (str): URL для загрузки данных о товарах
    - file (file): файл с данными о товарах

    Возвращает:
    - status (str): статус импорта
    - message (str): сообщение об успешном или неудачном импорте
    """
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        summary='Импорт товаров от поставщика',
        description='Импортирует товары в систему через указанный URL или загруженный файл.',
        parameters=[
            OpenApiParameter(name='url', description='URL файла с данными товаров', type=str, required=False),
            OpenApiParameter(name='file', description='Файл с данными товаров', type='file', required=False),
        ],
        request=None,  # Так как используются form-data, детали указываются в parameters
        responses={
            200: OpenApiResponse(description='Товары успешно импортированы'),
            400: OpenApiResponse(description='Неверные данные или ошибка при импорте'),
            403: OpenApiResponse(description='Доступ запрещен')
        }
    )
    def post(self, request):
        user = request.user

        if not user.is_superuser and user.type != "shop":
            return JsonResponse(
                {
                    "status": False,
                    "error": "Access denied. Only shops can import products.",
                },
                status=403,
            )

        url = request.data.get("url")
        file = request.FILES.get("file")

        if not url and not file:
            return JsonResponse(
                {"status": False, "error": "URL or file is required."}, status=400
            )

        try:
            if url:
                validate_url = URLValidator()
                validate_url(url)
                response = requests.get(url)
                response.raise_for_status()
                data = yaml.safe_load(response.content)
            elif file:
                data = yaml.safe_load(file.read())
        except ValidationError as e:
            return JsonResponse({"status": False, "error": "Invalid URL."}, status=400)
        except requests.RequestException as e:
            return JsonResponse(
                {"status": False, "error": "Failed to fetch the file from URL."},
                status=400,
            )
        except yaml.YAMLError as e:
            return JsonResponse(
                {"status": False, "error": "Invalid YAML file."}, status=400
            )

        with transaction.atomic():
            try:
                shop, created = Shop.objects.get_or_create(name=data["shop"], user=user)
                if created:
                    shop.url = url or ""
                    shop.save()

                categories = data.get("categories", [])
                for category_data in categories:
                    category, _ = Category.objects.get_or_create(
                        id=category_data["id"], defaults={"name": category_data["name"]}
                    )
                    category.shops.add(shop)
                    category.save()

                goods = data.get("goods", [])
                for item in goods:
                    product, _ = Product.objects.get_or_create(
                        name=item["name"], defaults={"category_id": item["category"]}
                    )

                    product_info = ProductInfo.objects.create(
                        product=product,
                        shop=shop,
                        name=item["model"],
                        quantity=item["quantity"],
                        price=item["price"],
                        price_rrc=item["price_rrc"],
                    )

                    parameters = item.get("parameters", {})
                    for param_name, param_value in parameters.items():
                        parameter, _ = Parameter.objects.get_or_create(name=param_name)
                        ProductParameter.objects.create(
                            product_info=product_info,
                            parameter=parameter,
                            value=param_value,
                        )

                return JsonResponse(
                    {"status": True, "message": "Products imported successfully."}
                )

            except Exception as e:
                return JsonResponse({"status": False, "error": str(e)}, status=500)
