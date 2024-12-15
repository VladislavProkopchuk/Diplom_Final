from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    LoginView,
    ProductInfoViewSet,
    CartView,
    ContactViewSet,
    ConfirmOrderView,
    OrderViewSet,
    ImportProducts,
)

router = DefaultRouter()
router.register(r"products", ProductInfoViewSet, basename="products")
router.register(r"contacts", ContactViewSet, basename="contacts")
router.register(r"orders", OrderViewSet, basename="orders")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("cart/", CartView.as_view(), name="cart"),
    path("confirm_order/", ConfirmOrderView.as_view(), name="confirm_order"),
    path("orders/confirm/", ConfirmOrderView.as_view(), name="confirm_order"),
    path("", include(router.urls)),
    path("import/", ImportProducts.as_view(), name="import_products"),
]
