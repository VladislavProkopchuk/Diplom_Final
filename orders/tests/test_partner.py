from http import HTTPStatus
from json import load as load_json
from os import path

import pytest
from yaml import load as load_yaml, FullLoader

from backend.models import ProductParameter
from tests import assert_success_response, assert_success_status, assert_fault_status


@pytest.mark.django_db
def test_partner_state_get(client, user_authorization_header, shop_factory):
    request_url = '/api/v1/partner/state'
    user, headers = user_authorization_header

    # проверяем неавторизованный вызов
    assert_fault_status(client.get(request_url), HTTPStatus.FORBIDDEN)

    if user.type == 'buyer':
        # проверяем вызов buyer
        assert_fault_status(client.get(request_url, headers=headers), HTTPStatus.FORBIDDEN)
    else:
        # проверяем отсутствие shop
        assert_fault_status(client.get(request_url, headers=headers))

        # проверяем успешный вызов shop
        shop = shop_factory(_quantity=1, user=user)[0]
        data = assert_success_response(client.get(request_url, headers=headers))
        assert data['name'] == shop.name


@pytest.mark.django_db
def test_partner_state_post(client, user_authorization_header, shop_factory):
    request_url = '/api/v1/partner/state'
    user, headers = user_authorization_header
    test_state = True

    # проверяем неавторизованный вызов
    data = {
        "param": str(test_state)
    }
    assert_fault_status(client.post(request_url, data=data), HTTPStatus.FORBIDDEN)

    if user.type == 'buyer':
        # проверяем вызов buyer
        assert_fault_status(client.post(request_url, data=data, headers=headers), HTTPStatus.FORBIDDEN)
    else:
        # проверяем обязательные аргументы
        assert_fault_status(client.post(request_url, data=data, headers=headers))

        # проверяем валидацию
        data = {
            "state": "da"
        }
        assert_fault_status(client.post(request_url, data=data, headers=headers))

        # проверяем успешный вызов shop
        data = {
            "state": str(test_state)
        }
        shop_factory(_quantity=1, user=user, state=not test_state)
        assert_success_status(client.post(request_url, data=data, headers=headers))


def test_partner_state_put_delete(client):
    request_url = '/api/v1/partner/state'

    # проверяем отсутствие методов
    data = {
        "state": "True"
    }
    assert_success_response(client.put(request_url, data=data), HTTPStatus.METHOD_NOT_ALLOWED)
    assert_success_response(client.delete(request_url, data=data), HTTPStatus.METHOD_NOT_ALLOWED)


@pytest.mark.django_db
def test_partner_orders_get(client, user_authorization_header, shop_factory, user_factory, order_factory,
                            order_item_factory, products_info_factory):
    request_url = '/api/v1/partner/orders'
    user, headers = user_authorization_header
    if user.type == 'shop':
        shop = shop_factory(_quantity=1, user=user)[0]
    else:
        shop = None

    # проверяем неавторизованный вызов
    assert_fault_status(client.get(request_url), HTTPStatus.FORBIDDEN)

    if user.type == 'buyer':
        # проверяем вызов buyer
        assert_fault_status(client.get(request_url, headers=headers), HTTPStatus.FORBIDDEN)
    else:
        # проверяем успешный вызов shop
        users = user_factory(_quantity=10, is_active=True, type='buyer')
        products_info = products_info_factory(shop=shop)

        orders = []
        product_in_order_count = len(products_info) // len(users)

        inx = 0
        for u in users:
            for i in range(inx, inx + product_in_order_count):
                order = order_factory(_quantity=1, user=u)[0]
                order_item_factory(_quantity=1, order=order, product_info=products_info[i])
                orders.append(order)
                inx += 1

        orders = [order for order in orders if order.state != 'basket']

        data = assert_success_response(client.get(request_url, headers=headers))
        assert len(data) == len(orders)
        for i, o in enumerate(data):
            assert o['id'] == orders[i].id


def test_partner_orders_post_put_delete(client):
    request_url = '/api/v1/partner/orders'

    # проверяем отсутствие методов
    data = {
        "state": "testState",
        "contact": "testContact"
    }
    assert_success_response(client.post(request_url, data=data), HTTPStatus.METHOD_NOT_ALLOWED)
    assert_success_response(client.put(request_url, data=data), HTTPStatus.METHOD_NOT_ALLOWED)
    assert_success_response(client.delete(request_url, data=data), HTTPStatus.METHOD_NOT_ALLOWED)


@pytest.mark.django_db
def test_partner_update_post(client, settings, user_authorization_header):
    request_url = '/api/v1/partner/update'
    user, headers = user_authorization_header

    # проверяем неавторизованный вызов
    data = {
        "url": "http://domain"
    }
    assert_fault_status(client.post(request_url, data=data), HTTPStatus.FORBIDDEN)

    if user.type == 'buyer':
        # проверяем вызов buyer
        assert_fault_status(client.post(request_url, data=data, headers=headers), HTTPStatus.FORBIDDEN)
    else:
        # проверяем обязательные параметры
        assert_fault_status(client.post(request_url, format='multipart', headers=headers))

        # проверяем формат запроса
        file_dir = path.join(path.dirname(settings.BASE_DIR), 'data')
        json_file_name = path.join(file_dir, 'shop1_fault.json')
        if path.exists(json_file_name):
            with open(json_file_name, 'rb') as json_file:
                assert_fault_status(
                    client.post(request_url, data={'file': json_file}, format='multipart', headers=headers))

        # проверяем успешный вызов
        yaml_file_name = path.join(file_dir, 'shop1.yaml')
        json_file_name = path.join(file_dir, 'shop1.json')

        if path.exists(yaml_file_name):
            with open(yaml_file_name, 'rb') as yaml_file:
                assert_success_status(
                    client.post(request_url, data={'file': yaml_file}, format='multipart', headers=headers))

            with open(yaml_file_name, 'r', encoding='utf8') as fh:
                data = load_yaml(fh, Loader=FullLoader)

            productparameter_list = ProductParameter.objects.filter(
                product_info__product__name=data['goods'][0]['name']).all()
            for product_parameter in productparameter_list:
                assert product_parameter.value == str(data['goods'][0]['parameters'][str(product_parameter.parameter)])

        if path.exists(json_file_name):
            with open(json_file_name, 'rb') as json_file:
                assert_success_status(
                    client.post(request_url, data={'file': json_file}, format='multipart', headers=headers))

            with open(json_file_name, 'r', encoding='utf8') as fh:
                data = load_json(fh)

            productparameter_list = ProductParameter.objects.filter(
                product_info__product__name=data['goods'][0]['name']).all()
            for product_parameter in productparameter_list:
                assert product_parameter.value == str(data['goods'][0]['parameters'][str(product_parameter.parameter)])


def test_partner_update_get_put_delete(client):
    request_url = '/api/v1/partner/update'

    # проверяем отсутствие методов
    data = {
        "url": "http://domain"
    }
    assert_success_response(client.get(request_url), HTTPStatus.METHOD_NOT_ALLOWED)
    assert_success_response(client.put(request_url, data=data), HTTPStatus.METHOD_NOT_ALLOWED)
    assert_success_response(client.delete(request_url, data=data), HTTPStatus.METHOD_NOT_ALLOWED)
