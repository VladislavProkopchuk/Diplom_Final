from rest_framework import permissions


class IsShop(permissions.BasePermission):
    message = "Только для магазинов"

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.type == "shop"


class IsBuyer(permissions.BasePermission):
    message = "Только для покупателей"

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.type == "buyer"
