from http import HTTPStatus

import pytest

from tests import assert_success_response


@pytest.mark.django_db
def test_shop_get(client, shop_factory):
    request_url = '/api/v1/shops'
    shops = shop_factory(_quantity=10)
    shops.sort(key=lambda s: s.name.upper(), reverse=True)

    # проверяем неавторизованный успешный вызов
    data = assert_success_response(client.get(request_url))
    assert len(data['results']) == len(shops)
    for i, s in enumerate(data['results']):
        assert s['name'] == str(shops[i])


def test_shop_post_put_delete(client):
    request_url = '/api/v1/shops'

    # проверяем отсутствие методов
    data = {
        "name": "testName",
        "url": "http://domain",
        "state": True
    }
    assert_success_response(client.post(request_url, data=data), HTTPStatus.METHOD_NOT_ALLOWED)
    assert_success_response(client.put(request_url, data=data), HTTPStatus.METHOD_NOT_ALLOWED)
    assert_success_response(client.delete(request_url, data=data), HTTPStatus.METHOD_NOT_ALLOWED)
