import random
import string

import pytest
from django.conf import settings
from model_bakery import baker
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from backend.models import Category, Product, ProductInfo
from backend.models import Order, OrderItem
from backend.models import Shop
from backend.models import User, Contact
from tests import USER_EMAIL, FROM_EMAIL


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture(scope="session", autouse=True)
def set_email_host_user():
    settings.EMAIL_HOST = None
    settings.EMAIL_HOST_USER = FROM_EMAIL
    settings.EMAIL_HOST_PASSWORD = None
    settings.EMAIL_PORT = None


@pytest.fixture(params=['shop', 'buyer'])
def user_create(request, django_user_model):
    user = django_user_model.objects.create_user(email=USER_EMAIL, password='P@$$sw0rd')
    user.is_active = True
    user.type = request.param
    user.save()
    return user


@pytest.fixture
def user_token(user_create):
    user = user_create
    Token.objects.create(user=user)
    return user, user.auth_token.key


@pytest.fixture
def user_login(user_create, client_obj):
    user = user_create
    client_obj.force_login(user)
    return user


@pytest.fixture
def user_authorization_header(user_token):
    user, token = user_token
    return user, {"Authorization": f"Token {token}"}


@pytest.fixture
def user_factory():
    def factory(*args, **kwargs):
        return baker.make(User, *args, **kwargs)

    return factory


@pytest.fixture
def contact_factory():
    def factory(*args, **kwargs):
        if 'type' in kwargs.keys():
            if kwargs['type'] == 'phone':
                kwargs['phone'] = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
            elif kwargs['type'] == 'address':
                kwargs['city'] = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
                kwargs['street'] = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
                kwargs['house'] = ''.join(random.choice(string.ascii_lowercase) for i in range(10))

        return baker.make(Contact, *args, **kwargs)

    return factory


@pytest.fixture
def shop_factory():
    def factory(*args, **kwargs):
        return baker.make(Shop, *args, **kwargs)

    return factory


@pytest.fixture
def category_factory():
    def factory(*args, **kwargs):
        return baker.make(Category, *args, **kwargs)

    return factory


@pytest.fixture
def order_factory():
    def factory(*args, **kwargs):
        return baker.make(Order, *args, **kwargs)

    return factory


@pytest.fixture
def order_item_factory():
    def factory(*args, **kwargs):
        if 'quantity' not in kwargs.keys():
            kwargs['quantity'] = random.randint(1, 10)
        return baker.make(OrderItem, *args, **kwargs)

    return factory


def get_param_value(value, key, **kwargs):
    if key in kwargs.keys():
        return kwargs.get(key)
    else:
        return value


@pytest.fixture
def products_info_factory(user_factory, shop_factory):
    def factory(*args, **kwargs):
        if 'user' in kwargs.keys():
            shop_users = [kwargs.get('user')]
        else:
            shop_users = user_factory(_quantity=3, is_active=True)

        if 'shop' in kwargs.keys():
            shops = [kwargs.get('shop')]
        else:
            shops = []
            for user in shop_users:
                shops += shop_factory(_quantity=1, user=user)

        categories = baker.make(Category, _quantity=5)
        products = []
        for category in categories:
            products += baker.make(Product, _quantity=2, category=category)

        products_info = []
        for shop in shops:
            for product in products:
                model_name = get_param_value(''.join(random.choice(string.ascii_lowercase) for i in range(10)),
                                             'model_name', **kwargs)
                pi_quantity = get_param_value(random.randint(100, 1000), 'quantity', **kwargs)
                pi_price = get_param_value(random.randint(2500, 100000), 'price', **kwargs)
                pi_price_rrc = get_param_value(pi_price + pi_price // 100 * 10, 'price_rrc', **kwargs)

                products_info += baker.make(ProductInfo, _quantity=2, model=model_name, product=product, shop=shop,
                                            quantity=pi_quantity, price=pi_price, price_rrc=pi_price_rrc)

        return products_info

    return factory
