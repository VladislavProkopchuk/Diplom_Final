import sys
import json
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import (
    Shop,
    Category,
    Product,
    ProductInfo,
    Parameter,
    ProductParameter,
    Order,
    OrderItem,
    Contact,
    CustomUser,
)


class ModelTestCase(TestCase):
    def setUp(self):
        # Создание пользователя с типом 'shop'
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            type="shop",
        )

        # Создание магазина
        self.shop = Shop.objects.create(
            name="Test Shop", url="http://testshop.com", user=self.user
        )

        # Создание категории
        self.category = Category.objects.create(name="Electronics")
        self.category.shops.add(self.shop)

        # Создание продукта
        self.product = Product.objects.create(name="Laptop", category=self.category)

        # Создание информации о продукте
        self.product_info = ProductInfo.objects.create(
            product=self.product,
            shop=self.shop,
            quantity=10,
            price=1000,
            price_rrc=1200,
        )

        # Создание параметра и добавление его к продукту
        self.parameter = Parameter.objects.create(name="Color")
        self.product_parameter = ProductParameter.objects.create(
            product_info=self.product_info, parameter=self.parameter, value="Black"
        )

        # Создание контакта пользователя
        self.contact = Contact.objects.create(
            user=self.user, type="email", value="contact@example.com"
        )

        # Создание заказа и добавление в него товара
        self.order = Order.objects.create(
            user=self.user, status="new", contact=self.contact
        )
        self.order_item = OrderItem.objects.create(
            order=self.order, product_info=self.product_info, quantity=1
        )

    def test_shop_creation(self):
        """
        Проверяет создание магазина.
        """
        self.assertEqual(self.shop.name, "Test Shop")
        self.assertTrue(self.shop.state)

    def test_category_creation(self):
        """
        Проверяет создание категории.
        """
        self.assertEqual(self.category.name, "Electronics")
        self.assertIn(self.shop, self.category.shops.all())

    def test_product_creation(self):
        """
        Проверяет создание продукта.
        """
        self.assertEqual(self.product.name, "Laptop")
        self.assertEqual(self.product.category, self.category)

    def test_product_info_creation(self):
        """
        Проверяет создание информации о продукте.
        """
        self.assertEqual(self.product_info.product, self.product)
        self.assertEqual(self.product_info.shop, self.shop)
        self.assertEqual(self.product_info.quantity, 10)
        self.assertEqual(self.product_info.price, 1000)
        self.assertEqual(self.product_info.price_rrc, 1200)
        self.assertTrue(self.product_info.is_available())

    def test_product_parameter_creation(self):
        """
        Проверяет создание параметра продукта.
        """
        self.assertEqual(self.product_parameter.product_info, self.product_info)
        self.assertEqual(self.product_parameter.parameter, self.parameter)
        self.assertEqual(self.product_parameter.value, "Black")

    def test_contact_creation(self):
        """
        Проверяет создание контакта пользователя.
        """
        self.assertEqual(self.contact.user, self.user)
        self.assertEqual(self.contact.type, "email")
        self.assertEqual(self.contact.value, "contact@example.com")

    def test_order_creation(self):
        """
        Проверяет создание заказа.
        """
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.status, "new")
        self.assertEqual(self.order.contact, self.contact)
        self.assertEqual(self.order.get_total_cost(), 1000)

    def test_order_item_creation(self):
        """
        Проверяет создание позиции заказа.
        """
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product_info, self.product_info)
        self.assertEqual(self.order_item.quantity, 1)
        self.assertEqual(self.order_item.get_cost(), 1000)

    def test_shop_get_active_products(self):
        """
        Проверяет получение активных продуктов магазина.
        """
        active_products = self.shop.get_active_products()
        self.assertIn(self.product_info, active_products)

    def test_category_get_products(self):
        """
        Проверяет получение продуктов категории.
        """
        products = self.category.get_products()
        self.assertIn(self.product, products)

    def test_product_get_info(self):
        """
        Проверяет получение информации о продукте.
        """
        product_infos = self.product.get_info()
        self.assertIn(self.product_info, product_infos)

    def test_product_info_is_available(self):
        """
        Проверяет доступность продукта.
        """
        self.assertTrue(self.product_info.is_available())

    def test_contact_get_user_contact_info(self):
        """
        Проверяет получение информации о контакте пользователя.
        """
        contact_info = self.contact.get_user_contact_info()
        self.assertEqual(contact_info, "email: contact@example.com")

    def test_order_get_total_cost(self):
        """
        Проверяет получение общей стоимости заказа.
        """
        total_cost = self.order.get_total_cost()
        self.assertEqual(total_cost, 1000)

    def test_order_item_get_cost(self):
        """
        Проверяет получение стоимости позиции заказа.
        """
        cost = self.order_item.get_cost()
        self.assertEqual(cost, 1000)


class ApiTestCase(APITestCase):
    def setUp(self):
        """
        Устанавливает начальные данные для тестов API.
        """
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            type="shop",
        )
        self.client.force_authenticate(user=self.user)
        self.shop = Shop.objects.create(
            name="Test Shop", url="http://testshop.com", user=self.user
        )
        self.category = Category.objects.create(name="Electronics")
        self.category.shops.add(self.shop)
        self.product = Product.objects.create(name="Laptop", category=self.category)
        self.product_info = ProductInfo.objects.create(
            product=self.product,
            shop=self.shop,
            quantity=10,
            price=1000,
            price_rrc=1200,
        )
        self.parameter = Parameter.objects.create(name="Color")
        self.product_parameter = ProductParameter.objects.create(
            product_info=self.product_info, parameter=self.parameter, value="Black"
        )
        self.contact = Contact.objects.create(
            user=self.user, type="email", value="contact@example.com"
        )
        self.order = Order.objects.create(
            user=self.user, status="basket", contact=self.contact
        )
        self.order_item = OrderItem.objects.create(
            order=self.order, product_info=self.product_info, quantity=1
        )

    def test_register(self):
        """
        Проверяет регистрацию нового пользователя.
        """
        url = reverse("register")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "newpassword",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "User created successfully")

    def test_login(self):
        """
        Проверяет авторизацию пользователя.
        """
        url = reverse("login")

        data = {"email": "testuser", "password": "testpassword"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "Login successful")

    def test_product_list(self):
        """
        Проверяет получение списка продуктов.
        """
        url = reverse("products-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_cart_add_item(self):
        """
        Проверяет добавление товара в корзину.
        """
        url = reverse("cart")
        data = {"product_info_id": self.product_info.id, "quantity": 1}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["ordered_items"]), 1)

    def test_cart_view(self):
        """
        Проверяет просмотр содержимого корзины.
        """
        url = reverse("cart")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["ordered_items"]), 1)

    def test_cart_remove_item(self):
        """
        Проверяет удаление товара из корзины.
        """
        url = reverse("cart")
        data = {"product_info_id": self.product_info.id}
        response = self.client.delete(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["ordered_items"]), 0)

    def test_contact_add(self):
        """
        Проверяет добавление контакта пользователя.
        """
        url = reverse("contacts-list")
        data = {
            "type": "phone",
            "value": "1234567890",
            "city": "Test City",
            "street": "Test Street",
            "house": "1",
            "structure": "",
            "building": "",
            "apartment": "",
            "phone": "1234567890",
            "user": self.user.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["value"], "1234567890")

    def test_confirm_order(self):
        """
        Проверяет подтверждение заказа.
        """
        url = reverse("confirm_order")
        data = {"order_id": self.order.id, "contact_id": self.contact.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "Order confirmed")

    def test_order_list(self):
        """
        Проверяет получение списка заказов.
        """
        self.order.status = "new"
        self.order.save()
        url = reverse("orders-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_create_order(self):
        """
        Проверяет создание нового заказа.
        """
        # Создание нового контакта
        contact_data = {
            "type": "email",
            "value": "new_contact@example.com",
            "city": "Test City",
            "street": "Test Street",
            "house": "1",
            "structure": "",
            "building": "",
            "apartment": "1",
            "phone": "1234567890",
            "user": self.user.id,
        }
        response = self.client.post(
            reverse("contacts-list"), contact_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        contact_id = response.data["id"]

        # Добавление товара в корзину
        cart_url = reverse("cart")
        cart_data = {"product_info_id": self.product_info.id, "quantity": 1}
        response = self.client.post(cart_url, cart_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Подтверждение заказа
        confirm_url = reverse("confirm_order")
        confirm_data = {"order_id": self.order.id, "contact_id": contact_id}
        response = self.client.post(confirm_url, confirm_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "Order confirmed")

    def test_contact_view(self):
        """
        Тест для просмотра списка контактов пользователя.
        """
        url = reverse('contacts-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertIn(self.contact.value, [contact['value'] for contact in response.data])

    def test_contact_delete(self):
        """
        Тест для удаления контакта пользователя.
        """
        url = reverse('contacts-detail', kwargs={'pk': self.contact.id})  # Используем "contacts-detail"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


if __name__ == "__main__":
    from django.test.utils import get_runner
    from django.conf import settings

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["__main__"])
    if failures:
        sys.exit(bool(failures))
