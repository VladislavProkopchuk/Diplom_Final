from datetime import datetime, timezone
from http import HTTPStatus

import pytest

from tests import FROM_EMAIL
from tests import assert_success_response, assert_success_status, assert_fault_status


@pytest.mark.django_db
def test_order_get(client, order_factory, user_authorization_header):
    request_url = '/api/v1/order'
    user, headers = user_authorization_header
    orders = order_factory(_quantity=10, user=user)
    orders = [order for order in orders if order.state != 'basket']

    # проверяем неавторизованный вызов
    assert_fault_status(client.get(request_url), HTTPStatus.FORBIDDEN)

    # проверяем успешный вызов
    data = assert_success_response(client.get(request_url, headers=headers))
    assert len(data) == len(orders)
    for i, o in enumerate(data):
        assert str(datetime.fromisoformat(o['dt']).astimezone(tz=timezone.utc)) == str(orders[i])


@pytest.mark.django_db
def test_order_post(client, user_authorization_header, set_email_host_user, mailoutbox, order_factory, contact_factory):
    request_url = '/api/v1/order'
    user, headers = user_authorization_header
    contact = contact_factory(_quantity=1, user=user)[0]
    order = order_factory(_quantity=1, user=user, state='basket')[0]

    # проверяем неавторизованный вызов
    data = {
        "id": "1"
    }
    assert_fault_status(client.post(request_url, data=data), HTTPStatus.FORBIDDEN)

    # проверяем обязательные аргументы
    assert_fault_status(client.post(request_url, data=data, headers=headers))

    # проверяем корректность значений аргументов
    data = {
        "id": "10",
        "contact": "10",
    }
    assert_fault_status(client.post(request_url, data=data, headers=headers))

    # проверяем успешный вызов
    data = {
        "id": str(order.id),
        "contact": str(contact.id),
    }
    assert_success_status(client.post(request_url, data=data, headers=headers))

    # проверяем отправку письма подтверждения
    assert len(mailoutbox) == 1
    message = mailoutbox[0]
    assert message.from_email == FROM_EMAIL, list(message.to) == [user.email]


def test_order_put_delete(client):
    request_url = '/api/v1/order'

    # проверяем отсутствие методов
    data = {
        "state": "testState",
        "contact": "testContact"
    }
    assert_success_response(client.put(request_url, data=data), HTTPStatus.METHOD_NOT_ALLOWED)
    assert_success_response(client.delete(request_url, data=data), HTTPStatus.METHOD_NOT_ALLOWED)
