from http import HTTPStatus

import pytest

from tests import assert_success_response


@pytest.mark.django_db
def test_category_get(client, category_factory):
    request_url = '/api/v1/categories'
    categories = category_factory(_quantity=10)
    categories.sort(key=lambda c: c.name.upper(), reverse=True)

    # проверяем неавторизованный успешный вызов
    data = assert_success_response(client.get(request_url))
    assert len(data['results']) == len(categories)
    for i, c in enumerate(data['results']):
        assert c['name'] == categories[i].name


def test_category_post_put_delete(client):
    request_url = '/api/v1/categories'

    # проверяем отсутствие методов
    data = {
        "name": "testName",
        "shops": ["1"]
    }
    assert_success_response(client.post(request_url, data=data), HTTPStatus.METHOD_NOT_ALLOWED)
    assert_success_response(client.put(request_url, data=data), HTTPStatus.METHOD_NOT_ALLOWED)
    assert_success_response(client.delete(request_url, data=data), HTTPStatus.METHOD_NOT_ALLOWED)
