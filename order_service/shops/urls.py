from django.urls import path

from . import views

urlpatterns = [
    path("partner/update", views.PartnerUpdate.as_view()),
    path("partner/state", views.PartnerState.as_view()),
    path("partner/orders", views.PartnerOrders.as_view()),
    path("shops", views.ShopList.as_view()),
    path("products", views.ProductInfoList.as_view()),
    path("categories", views.CategoryList.as_view()),
    path("basket", views.Basket.as_view()),
    path("orders", views.Orders.as_view()),
]
