from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from backend.models import User, Contact
from backend.signals import new_user_registered_signal
from tests import USER_EMAIL, FROM_EMAIL
from tests import assert_success_response, assert_success_status, assert_fault_status


@pytest.mark.django_db
def test_createsuperuser():
    # проверяем валидацию
    with pytest.raises(ValueError):
        get_user_model().objects.create_superuser('', 'password')
    with pytest.raises(ValueError):
        get_user_model().objects.create_superuser('admin@myproject.com', 'password', is_staff=False)
    with pytest.raises(ValueError):
        get_user_model().objects.create_superuser('admin@myproject.com', 'password', is_superuser=False)

    # проверяем успешный вызов
    get_user_model().objects.create_superuser('admin@myproject.com', 'password')
    user = User.objects.all()[0]
    assert user.is_superuser


@pytest.mark.parametrize(['user_email', 'user_type'], (('shop' + USER_EMAIL, 'shop'),
                                                       ('buyer' + USER_EMAIL, 'buyer')))
@pytest.mark.django_db
def test_user_register_post(client, user_email, user_type):
    request_url = '/api/v1/user/register'
    test_username = 'testUsername'

    # проверяем обязательные аргументы
    data = {
        "email": "",
        "username": test_username,
        "type": user_type
    }
    assert_fault_status(client.post(request_url, data=data))

    # проверяем пароль на сложность
    data = {
        "email": "",
        "first_name": "testFirstname",
        "last_name": "testLastname",
        "password": "t",
        "company": "testCompany",
        "position": "testPosition",
        "username": test_username,
        "type": user_type
    }
    assert_fault_status(client.post(request_url, data=data))

    # проверяем валидацию
    data["password"] = "testPassword"
    assert_fault_status(client.post(request_url, data=data))

    # проверяем успешный вызов
    data["email"] = user_email
    assert_success_status(client.post(request_url, data=data))

    users = User.objects.all()
    assert len(users) == 1
    assert users[0].email == user_email


@pytest.mark.django_db
def test_user_confirm_post(client, set_email_host_user, mailoutbox, user_factory):
    request_url = '/api/v1/user/register/confirm'
    user = user_factory(_quantity=1)[0]
    new_user_registered_signal(user.id)

    # проверяем отправку письма подтверждения
    assert len(mailoutbox) == 1
    message = mailoutbox[0]
    assert message.from_email == FROM_EMAIL, list(message.to) == [user.email]

    test_token = message.body

    # проверяем обязательные аргументы
    data = {
        "email": user.email
    }
    assert_fault_status(client.post(request_url, data=data))

    # проверяем некорректный токен
    data = {
        "email": user.email,
        "token": "token"
    }
    assert_fault_status(client.post(request_url, data=data))

    # проверяем успешный вызов
    data["token"] = test_token
    assert_success_status(client.post(request_url, data=data))


@pytest.mark.django_db
def test_user_login_post(client, user_factory):
    request_url = '/api/v1/user/login'
    user = user_factory(_quantity=1)[0]
    user_password = user.password
    user.set_password(user_password)
    user.save()

    # проверяем обязательные аргументы
    data = {
        "email": user.email
    }
    assert_fault_status(client.post(request_url, data=data))

    # проверяем некорректную авторизацию
    data = {
        "email": user.email,
        "password": ""
    }
    assert_fault_status(client.post(request_url, data=data))

    # проверяем деактевированного пользователя
    data["password"] = user_password
    assert_fault_status(client.post(request_url, data=data))

    # проверяем успешный вызов
    user.is_active = True
    user.save()
    data = assert_success_status(client.post(request_url, data=data))
    assert data['Token'] == user.auth_token.key


@pytest.mark.django_db
def test_user_password_reset_and_confirm_post(client, set_email_host_user, mailoutbox, user_factory):
    user = user_factory(_quantity=1)[0]
    user.is_active = True
    user.save()
    user_password = 'M9SoNoaFYB3RbTTC7YQH'

    # проверяем успешный вызов reset
    data = {
        "email": user.email
    }
    data = assert_success_response(client.post('/api/v1/user/password_reset', data=data))
    assert data['status'] == 'OK'

    # проверяем отправку письма подтверждения
    assert len(mailoutbox) == 1
    message = mailoutbox[0]
    assert message.from_email == FROM_EMAIL, list(message.to) == [user.email]

    test_token = message.body

    # проверяем успешный вызов confirm
    data = {
        "password": user_password,
        "token": test_token
    }
    data = assert_success_response(client.post('/api/v1/user/password_reset/confirm', data=data))
    assert data['status'] == 'OK'

    user = User.objects.get(pk=user.id)
    assert user.check_password(user_password)


@pytest.mark.django_db
def test_user_details_get(client, user_authorization_header):
    request_url = '/api/v1/user/details'
    user, headers = user_authorization_header

    # проверяем неавторизованный вызов
    assert_fault_status(client.get(request_url), HTTPStatus.FORBIDDEN)

    # проверяем успешный вызов
    data = assert_success_response(client.get(request_url, headers=headers))
    assert data['email'] == user.email


@pytest.mark.django_db
def test_user_details_post(client, user_authorization_header):
    request_url = '/api/v1/user/details'
    user, headers = user_authorization_header
    test_password = 'testUsername'

    # проверяем неавторизованный вызов
    data = {
        "email": "",
        "first_name": "testFirstname",
        "last_name": "testLastname",
        "password": "p",
        "company": "testCompany",
        "position": "testPosition"
    }
    assert_fault_status(client.post(request_url, data=data), HTTPStatus.FORBIDDEN)

    # проверяем пароль на сложность
    assert_fault_status(client.post(request_url, data=data, headers=headers))

    # проверяем валидацию
    data["password"] = test_password
    assert_fault_status(client.post(request_url, data=data, headers=headers))

    # проверяем успешный вызов
    data["email"] = user.email
    assert_success_status(client.post(request_url, data=data, headers=headers))


@pytest.mark.django_db
def test_user_contact_phone_save(client, user_create, contact_factory):
    user = user_create
    contacts = contact_factory(_quantity=1, user=user, type='phone')

    # проверяем успешное добавление
    assert len(contacts) == 1

    # проверяем валидацию при следующем добавлении
    with pytest.raises(ValidationError) as exc_info:
        contacts += contact_factory(_quantity=1, user=user, type='phone')
    assert exc_info.type is ValidationError


@pytest.mark.django_db
def test_user_contact_get(client, user_authorization_header, contact_factory):
    request_url = '/api/v1/user/contact'
    user, headers = user_authorization_header
    contacts = contact_factory(_quantity=10, user=user, type='address')
    contacts += contact_factory(_quantity=1, user=user, type='phone')

    # проверяем неавторизованный вызов
    assert_fault_status(client.get(request_url), HTTPStatus.FORBIDDEN)

    # проверяем успешный вызов
    data = assert_success_response(client.get(request_url, headers=headers))
    assert len(data) == len(contacts)
    for i, c in enumerate(data):
        if contacts[i].type == 'phone':
            check_str = f"{c['phone']}".strip()
        else:
            check_str = f"{c['city']} {c['street']} {c['house']}".strip()
        assert check_str == str(contacts[i])


@pytest.mark.parametrize('contact_type', ('phone', 'address'))
@pytest.mark.django_db
def test_user_contact_post(client, user_authorization_header, contact_factory, contact_type):
    request_url = '/api/v1/user/contact'
    user, headers = user_authorization_header
    test_street = 'testStreet'

    # проверяем неавторизованный вызов
    data = {
        "street": "testStreet",
        "house": "testHouse",
        "structure": "testStruct",
        "building": "testBuilding",
        "apartment": "testApartment"
    }
    assert_fault_status(client.post(request_url, data=data), HTTPStatus.FORBIDDEN)

    # проверяем обязательные аргументы
    assert_fault_status(client.post(request_url, data=data, headers=headers))

    # проверяем валидацию
    if contact_type == 'address':
        data["city"] = ""
        data["phone"] = ""
    assert_fault_status(client.post(request_url, data=data, headers=headers))

    # проверяем успешный вызов
    if contact_type == 'phone':
        data["city"] = ""
        data["phone"] = "testPhone"
    elif contact_type == 'address':
        data["city"] = "testCity"
        data["phone"] = ""
    data = assert_success_response(client.post(request_url, data=data, headers=headers))
    assert len(data) == 1

    contacts = Contact.objects.filter(user=user.id).all()
    assert len(contacts) == 1
    assert contacts[0].street == test_street


@pytest.mark.django_db
def test_user_contact_put(client, user_authorization_header, contact_factory):
    request_url = '/api/v1/user/contact'
    user, headers = user_authorization_header
    contact = contact_factory(_quantity=1, user=user, type='address')[0]
    test_city = 'testCity'

    # проверяем неавторизованный вызов
    data = {
        "city": test_city,
        "street": contact.street,
        "house": contact.house,
        "structure": contact.structure,
        "building": contact.building,
        "apartment": contact.apartment
    }
    assert_fault_status(client.put(request_url, data=data), HTTPStatus.FORBIDDEN)

    # проверяем обязательные аргументы
    assert_fault_status(client.put(request_url, data=data, headers=headers))

    # проверяем успешный вызов
    data["id"] = str(contact.id)
    assert_success_status(client.put(request_url, data=data, headers=headers))

    contact = Contact.objects.get(pk=contact.id)
    assert contact.city == test_city

    # проверяем валидацию
    data["city"] = ""
    assert_fault_status(client.put(request_url, data=data, headers=headers))

    contact = contact_factory(_quantity=1, user=user, type='phone')[0]
    data["id"] = str(contact.id)
    data["phone"] = ""
    assert_fault_status(client.put(request_url, data=data, headers=headers))


@pytest.mark.django_db
def test_user_contact_delete(client, user_authorization_header, contact_factory):
    request_url = '/api/v1/user/contact'
    user, headers = user_authorization_header
    contacts = contact_factory(_quantity=5, user=user, type='address')

    # проверяем неавторизованный вызов
    data = {
        "id": "0"
    }
    assert_fault_status(client.delete(request_url, data=data), HTTPStatus.FORBIDDEN)

    # проверяем обязательные аргументы
    assert_fault_status(client.delete(request_url, data=data, headers=headers))

    # проверяем успешный вызов
    data = {
        "items": ','.join([str(contact.id) for contact in contacts])
    }
    data = assert_success_status(client.delete(request_url, data=data, headers=headers))
    assert data['Удалено объектов'] == len(contacts)
