"""
Классы для ORM Django
"""
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ("shop", "Shop"),
        ("customer", "Customer"),
    )
    type = models.CharField(
        max_length=10, choices=USER_TYPE_CHOICES, default="customer"
    )


class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    url = models.URLField(verbose_name="Ссылка", null=True, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    state = models.BooleanField(verbose_name="Статус получения заказов", default=True)

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Список магазинов"
        ordering = ("-name",)

    def __str__(self):
        return self.name

    def get_active_products(self):
        return self.product_infos.filter(quantity__gt=0)


class Category(models.Model):
    name = models.CharField(max_length=40, verbose_name="Название")
    shops = models.ManyToManyField(
        Shop, verbose_name="Магазины", related_name="categories", blank=True
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Список категорий"
        ordering = ("-name",)

    def __str__(self):
        return self.name

    def get_products(self):
        return self.products.all()


class Product(models.Model):
    name = models.CharField(max_length=80, verbose_name="Название")
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        related_name="products",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Список продуктов"
        ordering = ("-name",)

    def __str__(self):
        return str(self.name)

    def get_info(self):
        return self.product_infos.all()


class ProductInfo(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="Продукт",
        related_name="product_infos",
        on_delete=models.CASCADE,
    )
    shop = models.ForeignKey(
        Shop,
        verbose_name="Магазин",
        related_name="product_infos",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=80, verbose_name="Название", blank=True)
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.PositiveIntegerField(verbose_name="Цена")
    price_rrc = models.PositiveIntegerField(verbose_name="Рекомендуемая розничная цена")

    class Meta:
        verbose_name = "Информация о продукте"
        verbose_name_plural = "Информационный список о продуктах"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "shop"], name="unique_product_info"
            ),
        ]

    def __str__(self):
        return f"{self.product.name} in {self.shop.name}"

    def is_available(self):
        return self.quantity > 0


class Parameter(models.Model):
    name = models.CharField(max_length=40, verbose_name="Название")

    class Meta:
        verbose_name = "Имя параметра"
        verbose_name_plural = "Список имен параметров"
        ordering = ("-name",)

    def __str__(self):
        return str(self.name)


class ProductParameter(models.Model):
    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name="Информация о продукте",
        related_name="product_parameters",
        on_delete=models.CASCADE,
    )
    parameter = models.ForeignKey(
        Parameter,
        verbose_name="Параметр",
        related_name="product_parameters",
        on_delete=models.CASCADE,
    )
    value = models.CharField(verbose_name="Значение", max_length=100)

    class Meta:
        verbose_name = "Параметр"
        verbose_name_plural = "Список параметров"
        constraints = [
            models.UniqueConstraint(
                fields=["product_info", "parameter"], name="unique_product_parameter"
            ),
        ]

    def __str__(self):
        return f"{self.parameter.name}: {self.value}"


class Contact(models.Model):
    CONTACT_TYPE_CHOICES = (
        ("phone", "Телефон"),
        ("email", "Email"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        related_name="contacts",
        on_delete=models.CASCADE,
    )
    type = models.CharField(
        verbose_name="Тип", choices=CONTACT_TYPE_CHOICES, max_length=5
    )
    value = models.CharField(max_length=100, verbose_name="Значение")
    city = models.CharField(max_length=50, verbose_name="Город", blank=True, null=True)
    street = models.CharField(
        max_length=100, verbose_name="Улица", blank=True, null=True
    )
    house = models.CharField(max_length=15, verbose_name="Дом", blank=True, null=True)
    structure = models.CharField(
        max_length=15, verbose_name="Корпус", blank=True, null=True
    )
    building = models.CharField(
        max_length=15, verbose_name="Строение", blank=True, null=True
    )
    apartment = models.CharField(
        max_length=15, verbose_name="Квартира", blank=True, null=True
    )
    phone = models.CharField(
        max_length=20, verbose_name="Телефон", blank=True, null=True
    )

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Список контактов"

    def __str__(self):
        return f"{self.type}: {self.value}"

    def get_user_contact_info(self):
        return f"{self.type}: {self.value}"


class Order(models.Model):
    STATUS_CHOICES = (
        ("basket", "Статус корзины"),
        ("new", "Новый"),
        ("confirmed", "Подтвержден"),
        ("assembled", "Собран"),
        ("sent", "Отправлен"),
        ("delivered", "Доставлен"),
        ("canceled", "Отменен"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        related_name="orders",
        on_delete=models.CASCADE,
    )
    dt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        verbose_name="Статус", choices=STATUS_CHOICES, max_length=15, default="basket"
    )
    contact = models.ForeignKey(
        Contact, verbose_name="Контакт", blank=True, null=True, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Список заказов"
        ordering = ("-dt",)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.ordered_items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name="Заказ",
        related_name="ordered_items",
        on_delete=models.CASCADE,
    )
    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name="Информация о продукте",
        related_name="ordered_items",
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Заказанная позиция"
        verbose_name_plural = "Список заказанных позиций"
        constraints = [
            models.UniqueConstraint(
                fields=["order", "product_info"], name="unique_order_item"
            ),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product_info.product.name} from" \
               f" {self.product_info.shop.name}"

    def get_cost(self):
        return self.product_info.price * self.quantity
