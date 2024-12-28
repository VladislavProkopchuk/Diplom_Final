from django.db import models
from order_service.users.models import User, Contact

STATE_CHOICES = (
    ("basket", "Статус корзины"),
    ("new", "Новый"),
)


class Shop(models.Model):
    name = models.CharField(verbose_name="Название", max_length=50)
    url = models.URLField(verbose_name="Ссылка", null=True, blank=True)
    user = models.OneToOneField(
        User,
        verbose_name="Пользователь",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    is_accepting_orders = models.BooleanField(
        verbose_name="Принимает заказы", default=True
    )

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Список магазинов"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=40, verbose_name="Название")
    shops = models.ManyToManyField(
        Shop, verbose_name="Магазины", related_name="categories", blank=True
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Список категорий"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(verbose_name="Название", max_length=80, unique=True)
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        related_name="products",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Список продуктов"
        ordering = ("name",)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    model = models.CharField(max_length=80, verbose_name="Модель", blank=True)
    external_id = models.PositiveIntegerField(verbose_name="Внешний ID")
    product = models.ForeignKey(
        Product,
        verbose_name="Продукт",
        related_name="product_infos",
        blank=True,
        on_delete=models.CASCADE,
    )
    shop = models.ForeignKey(
        Shop,
        verbose_name="Магазин",
        related_name="product_infos",
        blank=True,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.PositiveIntegerField(verbose_name="Цена")
    price_rrc = models.PositiveIntegerField(verbose_name="Рекомендуемая розничная цена")

    class Meta:
        verbose_name = "Информация о продукте"
        verbose_name_plural = "Информационный список о продуктах"
        constraints = [
            models.UniqueConstraint(
                fields=["shop", "external_id"], name="unique_product_info"
            ),
        ]

    def __str__(self):
        return self.model


class Parameter(models.Model):
    name = models.CharField(verbose_name="Название", max_length=40, unique=True)

    class Meta:
        verbose_name = "Имя параметра"
        verbose_name_plural = "Список имен параметров"
        ordering = ("name",)

    def __str__(self):
        return self.name


class ProductInfoParameter(models.Model):
    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name="Информация о продукте",
        related_name="product_info_parameters",
        on_delete=models.CASCADE,
    )
    parameter = models.ForeignKey(
        Parameter,
        verbose_name="Параметр",
        related_name="product_info_parameters",
        on_delete=models.CASCADE,
    )
    value = models.CharField(verbose_name="Значение", max_length=100)

    class Meta:
        verbose_name = "Параметр"
        verbose_name_plural = "Список параметров"
        constraints = [
            models.UniqueConstraint(
                fields=["product_info", "parameter"],
                name="unique_product_info_parameter",
            ),
        ]


class Order(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="orders",
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    state = models.CharField(
        verbose_name="Статус", choices=STATE_CHOICES, max_length=15
    )
    contact = models.ForeignKey(
        Contact, verbose_name="Контакт", blank=True, null=True, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Список заказ"
        ordering = ("-created_at",)

    def __str__(self):
        return str(self.created_at)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name="Заказ",
        related_name="ordered_items",
        blank=True,
        on_delete=models.CASCADE,
    )

    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name="Информация о продукте",
        related_name="ordered_items",
        blank=True,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Заказанная позиция"
        verbose_name_plural = "Список заказанных позиций"
        constraints = [
            models.UniqueConstraint(
                fields=["order_id", "product_info"], name="unique_order_item"
            ),
        ]

    @property
    def total(self):
        return self.quantity * self.product_info.price
