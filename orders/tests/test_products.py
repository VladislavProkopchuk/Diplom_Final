from http import HTTPStatus

import pytest

from tests import assert_success_response


@pytest.mark.django_db
def test_product_get(client, products_info_factory):
    request_url = '/api/v1/products'
    products_info = products_info_factory()

    # проверяем неавторизованный успешный вызов
    data = assert_success_response(client.get(request_url))

    assert data[0]['product']['name'] == str(list(filter(lambda x: x.id == data[0]['id'], products_info))[0].product)
    for i, s in enumerate(data):
        assert s['id'] in [product_info.id for product_info in products_info]

    # проверяем неавторизованный успешный вызов с параметром shop_id
    shop_id = products_info[0].shop_id
    data = {
        "shop_id": shop_id
    }
    data = assert_success_response(client.get(request_url, data=data))
    assert len(data) == len([product_info for product_info in products_info if product_info.shop_id == shop_id])

    # проверяем неавторизованный успешный вызов с параметром category_id
    category_id = products_info[0].product.category_id
    data = {
        "category_id": category_id
    }
    data = assert_success_response(client.get(request_url, data=data))
    assert len(data) == len(
        [product_info for product_info in products_info if product_info.product.category_id == category_id])


def test_product_post_put_delete(client):
    request_url = '/api/v1/products'

    # проверяем отсутствие методов
    data = {
        "name": "testName"
    }
    assert_success_response(client.post(request_url, data=data), HTTPStatus.METHOD_NOT_ALLOWED)
    assert_success_response(client.put(request_url, data=data), HTTPStatus.METHOD_NOT_ALLOWED)
    assert_success_response(client.delete(request_url, data=data), HTTPStatus.METHOD_NOT_ALLOWED)
