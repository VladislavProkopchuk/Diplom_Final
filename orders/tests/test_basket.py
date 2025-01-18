from http import HTTPStatus

import pytest

from tests import assert_success_response, assert_success_status, assert_fault_status


def create_basket_order(user, order_factory, order_item_factory, products_info_factory):
    products_info = products_info_factory()

    order = order_factory(_quantity=1, user=user, state='basket')[0]
    for product_info in products_info:
        order_item_factory(_quantity=1, order=order, product_info=product_info)

    return order


@pytest.mark.django_db
def test_basket_get(client, user_authorization_header, order_factory, order_item_factory, products_info_factory):
    request_url = '/api/v1/basket'
    user, headers = user_authorization_header

    # проверяем неавторизованный вызов
    assert_fault_status(client.get(request_url), HTTPStatus.FORBIDDEN)

    # проверяем успешный вызов
    order = create_basket_order(user, order_factory, order_item_factory, products_info_factory)

    data = assert_success_response(client.get(request_url, headers=headers))
    assert len(data) == 1
    assert data[0]['id'] == order.id


@pytest.mark.django_db
def test_basket_post(client, user_authorization_header, products_info_factory):
    request_url = '/api/v1/basket'
    user, headers = user_authorization_header

    # проверяем неавторизованный вызов
    assert_fault_status(client.post(request_url), HTTPStatus.FORBIDDEN)

    # проверяем обязательные аргументы
    data = {"params": ""}
    assert_fault_status(client.post(request_url, data=data, headers=headers))

    # проверяем формат запроса
    data = {"items": {"product_info": 1}}
    assert_fault_status(client.post(request_url, data=data, headers=headers))

    # проверяем валидацию
    data = {"items": [{"product_info": 1}, {"product_info": 2}]}
    assert_fault_status(client.post(request_url, data=data, headers=headers))

    # проверяем успешный вызов
    products_info = products_info_factory()
    data = {"items": [{"product_info": products_info[0].id, "quantity": 1},
                      {"product_info": products_info[1].id, "quantity": 1},
                      {"product_info": products_info[2].id, "quantity": 2}]}

    response_data = assert_success_status(client.post(request_url, data=data, headers=headers))
    assert response_data['Создано объектов'] == len(data['items'])


@pytest.mark.django_db
def test_basket_put(client, user_authorization_header, order_factory, order_item_factory, products_info_factory):
    request_url = '/api/v1/basket'
    user, headers = user_authorization_header

    # проверяем неавторизованный вызов
    assert_fault_status(client.put(request_url), HTTPStatus.FORBIDDEN)

    # проверяем обязательные аргументы
    data = {"params": ""}
    assert_fault_status(client.put(request_url, data=data, headers=headers))

    # проверяем формат запроса
    data = {"items": {"product_info": 1}}
    assert_fault_status(client.put(request_url, data=data, headers=headers))

    # проверяем успешный вызов
    order = create_basket_order(user, order_factory, order_item_factory, products_info_factory)
    order_items = order.ordered_items.model.objects.all()[:3]
    data = {"items": [{"id": order_items[0].id, "quantity": 5}, {"id": order_items[1].id, "quantity": 6},
                      {"id": order_items[2].id, "quantity": 7}]}

    response_data = assert_success_status(client.put(request_url, data=data, headers=headers))
    assert response_data['Обновлено объектов'] == len(data['items'])


@pytest.mark.django_db
def test_basket_delete(client, user_authorization_header, order_factory, order_item_factory, products_info_factory):
    request_url = '/api/v1/basket'
    user, headers = user_authorization_header

    # проверяем неавторизованный вызов
    assert_fault_status(client.delete(request_url), HTTPStatus.FORBIDDEN)

    # проверяем обязательные аргументы
    data = {"params": ""}
    assert_fault_status(client.delete(request_url, data=data, headers=headers))

    # проверяем успешный вызов
    order = create_basket_order(user, order_factory, order_item_factory, products_info_factory)
    order_items = order.ordered_items.model.objects.all()[:3]
    data = {"items": f"{order_items[0].id}, {order_items[1].id}, {order_items[2].id}"}

    data = assert_success_status(client.delete(request_url, data=data, headers=headers))
    assert data['Удалено объектов'] == 3
